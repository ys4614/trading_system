import os
import datetime
import time
import pandas as pd
import logging

import logging

logger = logging.getLogger("trading_system").getChild(__name__)


from util import round_time
from util import trading_time
from util import trading_execute
from datasource import make_data_frame as mdf
from datasource import trade_api

import global_value as g

# 株価取得間隔時間（単位：秒）
WAIT_TIME = 15
WAIT_NEXT_TRADE_SECONDS = 60

# RSI指標
RSI_BUY_IN = 25
RSI_BUY_OUT = 75
RSI_SELL_IN = 80
RSI_SELL_OUT = 30

# バージョン
logic_name = "1.0.1.apple"

# トレード実施有無
# trade_execute = True
trade_execute = False


def trader_func(token, stock_code, qty=100):
    symbol_name = ""

    # 現在値
    close_value = 0

    # 取引中フラグ
    last_order_id_buy = None
    last_order_id_sell = None

    trade_value = 0
    trade_value2 = 0

    trade_time = datetime.datetime.now()

    # interval = ["15s", "30s", "1m", "5m", "15m"]
    interval = ["5m"]
    d = {name: pd.DataFrame() for name in interval}
    # d = {name: pd.DataFrame() for name in g.data_pattern["interval"]}

    current_directory = os.path.dirname(os.path.abspath(__file__))
    prefilename = current_directory + "/data/" + stock_code + "-"

    while True:
        current_time = datetime.datetime.now().time()

        # 取引時間帯か確認
        if trading_time.trading_time():
            # 現在の板情報を取得
            (
                close_value,
                trading_volume,
                symbol_name,
                change_previous_close_per,
                high_price,
                low_price,
                current_price_time,
            ) = trade_api.get_board(token, stock_code)

            # None(データ無し、寄り付き前)の場合は待つ
            if close_value is None or trading_volume is None:
                time.sleep(WAIT_TIME)
                continue

            # ファイル更新
            for name, df in d.items():
                filename = prefilename + name + ".csv"
                df = pd.read_csv(filename)  # CSVファイルから株価データを呼び出し

                if name == "1d":
                    df = df.set_index("Date")  # データフレームを元の形に直す
                else:
                    df = df.set_index("Datetime")  # データフレームを元の形に直す

                dt_now_jst_aware = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
                dt_now_jst_aware = dt_now_jst_aware.replace(microsecond=0)
                match name:
                    case "15s":
                        dt_now_jst_aware = round_time.round_to_nearest_seconds(dt_now_jst_aware, 15)
                    case "30s":
                        dt_now_jst_aware = round_time.round_to_nearest_seconds(dt_now_jst_aware, 30)
                    case "1m":
                        dt_now_jst_aware = round_time.round_to_nearest_minutes(dt_now_jst_aware, 1)
                    case "5m":
                        dt_now_jst_aware = round_time.round_to_nearest_minutes(dt_now_jst_aware, 5)
                    case "15m":
                        dt_now_jst_aware = round_time.round_to_nearest_minutes(dt_now_jst_aware, 15)
                    case "60m":
                        dt_now_jst_aware = dt_now_jst_aware.replace(minute=0)
                    case "1d":
                        dt_now_jst_aware = dt_now_jst_aware.replace(hour=0, minute=0)

                tstr = dt_now_jst_aware.strftime("%Y-%m-%d %H:%M:%S") + "+09:00"
                # 以下のコードはエラーとなるため、上記のコードにしている。
                # tstr = dt_now_jst_aware.strftime("%Y-%m-%d %H:%M:%S%z")
                if tstr in df.index:
                    # 最下行を削除 (元のDataFrameを変更)
                    df.drop(df.index[-1], inplace=True)
                    df.loc[dt_now_jst_aware] = 0
                    df.at[dt_now_jst_aware, "Adj Close"] = close_value
                else:
                    df.loc[dt_now_jst_aware] = 0
                    df.at[dt_now_jst_aware, "Adj Close"] = close_value

                # MACD、移動平均の算出
                df = mdf.update_df(df, name)

                # CSVファイルに株価データを保存
                df.to_csv(filename)

                # トレードインしてから、一定時間は判定しない。
                if (last_order_id_buy != None or last_order_id_sell != None) and trading_time.check_elapsed_time(
                    trade_time, WAIT_NEXT_TRADE_SECONDS
                ) == False:
                    time.sleep(WAIT_TIME)
                    continue

                # トレードイン判定
                if last_order_id_buy == None and last_order_id_sell == None:
                    # 買い判定
                    # RSIが30以下
                    if df.iloc[-1]["RSI"] <= RSI_BUY_IN:
                        # MACDがGC
                        if df.iloc[-1]["macdhist"] > 0.0:
                            logger.info(f"{stock_code},{symbol_name},{name},MACD,買い,{str(close_value)}")
                            last_order_id_buy, trade_value, trade_time = order_buy(
                                token, symbol_name, stock_code, close_value, qty
                            )

                    # 移動平均が上昇中かつ移動平均のGC
                    if df.iloc[-1]["sma01"] > df.iloc[-1]["sma02"] > df.iloc[-1]["sma03"]:
                        if (
                            df.iloc[-2]["sma01"] <= df.iloc[-2]["sma02"]
                            or df.iloc[-2]["sma01"] <= df.iloc[-2]["sma03"]
                            or df.iloc[-2]["sma02"] <= df.iloc[-2]["sma03"]
                        ):
                            logger.info(f"{stock_code},{symbol_name},{name},SMA,買い,{str(close_value)}")
                            last_order_id_buy, trade_value, trade_time = order_buy(
                                token, symbol_name, stock_code, close_value, qty
                            )

                    # 売り判定
                    # RSIが70以上
                    if df.iloc[-1]["RSI"] >= RSI_SELL_IN:
                        # MACDがDC
                        if df.iloc[-1]["macdhist"] < 0.0:
                            logger.info(f"{stock_code},{symbol_name},{name},MACD,売り,{str(close_value)}")
                            last_order_id_sell, trade_value2, trade_time = order_sell(
                                token, symbol_name, stock_code, close_value, qty
                            )

                    # 移動平均が下降中かつ移動平均のDC
                    if df.iloc[-1]["sma01"] < df.iloc[-1]["sma02"]:
                        if df.iloc[-2]["sma01"] >= df.iloc[-2]["sma02"]:
                            logger.info(f"{stock_code},{symbol_name},{name},SMA,売り,{str(close_value)}")
                            last_order_id_sell, trade_value2, trade_time = order_sell(
                                token, symbol_name, stock_code, close_value, qty
                            )

                # トレードアウト判定
                else:
                    # 買い返済判定
                    if last_order_id_buy != None:
                        payback = False

                        # 移動平均が下降
                        if df.iloc[-1]["sma01"] < df.iloc[-1]["sma02"]:
                            payback = True
                            # logger.info(f"{symbol_name}:{stock_code}:信用買い返済。RSI,MACD")

                        if payback == True:
                            if trade_value < close_value:
                                diff_value = close_value - trade_value
                                summary = symbol_name + ",信用買い利確," + str(diff_value)
                            elif trade_value > close_value:
                                diff_value = close_value - trade_value
                                summary = symbol_name + ",信用買い損切," + str(diff_value)
                            else:
                                diff_value = 0
                                summary = symbol_name + ",信用買い返済,0"

                            mailText = summary + ",値," + str(close_value)

                            trading_execute.transaction_execute_buy_out(
                                logic_name,
                                stock_code,
                                symbol_name,
                                close_value,
                                mailText,
                                diff_value,
                            )

                            if trade_execute:
                                try:
                                    exist_order = trade_api.is_buy_order(token, stock_code)
                                    if exist_order:
                                        logger.info("買い注文が約定していなかった場合のために買い注文があれば取消")
                                        trade_api.all_cancel_order(token, stock_code)

                                    trade_api.all_close_margin(token, stock_code, 20, close_value)
                                except Exception as e:
                                    logger.info("返済で例外をキャッチしました。")
                                    print(e)
                                    last_order_id_buy = None

                            last_order_id_buy = None

                    # 売りでイン中
                    if last_order_id_sell != None:
                        payback = False

                        # 移動平均が上昇
                        if df.iloc[-1]["sma01"] > df.iloc[-1]["sma02"]:
                            payback = True
                            # logger.info(f"{symbol_name}:{stock_code}:空売り返済。RSI,MACD")

                        if payback == True:
                            if trade_value2 > close_value:
                                diff_value = trade_value2 - close_value
                                summary = symbol_name + ",空売り利確," + str(diff_value)
                            elif trade_value2 < close_value:
                                diff_value = trade_value2 - close_value
                                summary = symbol_name + ",空売り損切," + str(diff_value)
                            else:
                                diff_value = 0
                                summary = symbol_name + ",空売り返済,0"

                            mailText = summary + ",値," + str(close_value)
                            trading_execute.transaction_execute_sell_out(
                                logic_name,
                                stock_code,
                                symbol_name,
                                close_value,
                                mailText,
                                diff_value,
                            )

                            if trade_execute:
                                try:
                                    exist_order = trade_api.is_sell_order(token, stock_code)
                                    if exist_order:
                                        logger.info("売り注文が約定していなかった場合のために買い注文があれば取消")
                                        trade_api.all_cancel_order(token, stock_code)

                                    trade_api.all_close_margin(token, stock_code, 20, close_value)
                                except Exception as e:
                                    logger.info("返済で例外をキャッチしました。")
                                    print(e)
                                    last_order_id_sell = None

                            last_order_id_sell = None

        else:
            # 終盤の強制決済　注文中の場合は取り消してから成り行き決済
            if trading_time.before_finish_time():
                if trade_execute:
                    logger.info("全てのデイトレ注文を取消\n---------------")
                    trade_api.all_cancel_order(token, stock_code)

                    logger.info("全ての信用ポジション返済\n---------------")
                    trade_api.all_close_margin(token, stock_code, 10, 0)

                break

        time.sleep(WAIT_TIME)


def order_buy(token, symbol_name, stock_code, close_value, qty):
    mailText = symbol_name + ",買い," + str(close_value)
    trading_execute.transaction_execute_buy_in(
        logic_name,
        stock_code,
        symbol_name,
        close_value,
        mailText,
    )
    trade_value = close_value
    trade_time = datetime.datetime.now()

    # 発注
    try:
        exist_order = trade_api.is_sell_order(token, stock_code)
        if exist_order:
            if trade_execute:
                logger.info("買い注文前に買い返済注文（売り）がある場合は、その注文を取り消してポジションを保持する。")
                trade_api.all_cancel_order(token, stock_code)
                last_order_id_buy = "Dummy Id"
        else:
            if trade_execute:
                content = trade_api.send_order_margin(
                    token=token,
                    symbol=stock_code,
                    side="buy",
                    qty=qty,
                    price=close_value,
                )
                result = content.get("Result")
                if result == 0:
                    last_order_id_buy = content.get("OrderId")
                else:
                    logger.info(f"発注エラー。result:{result}")
                    print(f"発注エラー。result:{result}")
            else:
                last_order_id_buy = "Dummy Id"

    except Exception as e:
        print(e)

    return last_order_id_buy, trade_value, trade_time


def order_sell(token, symbol_name, stock_code, close_value, qty):
    mailText = symbol_name + ",売り," + str(close_value)
    trading_execute.transaction_execute_sell_in(
        logic_name,
        stock_code,
        symbol_name,
        close_value,
        mailText,
    )
    trade_value2 = close_value
    trade_time = datetime.datetime.now()

    # 発注
    try:
        exist_order = trade_api.is_buy_order(token, stock_code)
        if exist_order:
            if trade_execute:
                logger.info("売り注文前に売り返済注文（買い）がある場合は、その注文を取り消してポジションを保持する。")
                trade_api.all_cancel_order(token, stock_code)
                last_order_id_sell = "Dummy Id"
        else:
            if trade_execute:
                content = trade_api.send_order_margin(
                    token=token,
                    symbol=stock_code,
                    side="sell",
                    qty=qty,
                    price=close_value,
                )
                result = content.get("Result")
                if result == 0:
                    last_order_id_sell = content.get("OrderId")
                else:
                    logger.info(f"発注エラー。result:{result}")
                    print(f"発注エラー。result:{result}")
            else:
                last_order_id_sell = "Dummy Id"

    except Exception as e:
        print(e)

    return last_order_id_sell, trade_value2, trade_time
