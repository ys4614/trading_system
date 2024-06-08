import time

from datasource import trade_api
from util import trading_time

# update interval(sec)
WAIT_TIME = 30

change_previous_close_per_nikkei = 0
change_previous_close_per_grow = 0


def update_index(token):
    while trading_time.trading_time():
        # 日経
        temp_stockcode = "1321"
        (
            close_value_market,
            trading_volume,
            symbol_name,
            change_previous_close_per_nikkei,
            high_price,
            low_price,
            current_price_time,
        ) = trade_api.get_board(token, temp_stockcode)

        # マザーズ
        temp_stockcode = "2516"
        (
            close_value_market,
            trading_volume,
            symbol_name,
            change_previous_close_per_grow,
            high_price,
            low_price,
            current_price_time,
        ) = trade_api.get_board(token, temp_stockcode)

        time.sleep(WAIT_TIME)


# 日経、マザーズの前日比から買い・売りの有効無効を判定
def judge_buy_sell(is_maza):
    is_Buy_Enable = True
    is_Sell_Enable = True

    # 日経
    if is_maza == False:
        change_previous_close_per = change_previous_close_per_nikkei
    # マザーズ
    else:
        change_previous_close_per = change_previous_close_per_grow

    # -1%以下の場合は地合い悪いため、買い無効。
    if change_previous_close_per <= -1.0:
        is_Buy_Enable = False

    # 1%以上の場合は地合い良いため、売り無効。
    elif change_previous_close_per >= 1.0:
        is_Sell_Enable = False

    return is_Buy_Enable, is_Sell_Enable
