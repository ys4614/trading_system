import sys
import urllib.request
import json
import os
import pandas as pd
import time

import logging

logger = logging.getLogger("trading_system").getChild(__name__)

# 本番環境
_host = "18080"

# テスト環境
# _host = "18081"

trading_pass = os.environ["ENV_KABU_PASS"]


# トークンを取得する関数
def generate_token(APIPassword):
    token_value = ""
    obj = {"APIPassword": APIPassword}
    json_data = json.dumps(obj).encode("utf8")
    url = f"http://localhost:{_host}/kabusapi/token"
    req = urllib.request.Request(url, json_data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as res:
            content = json.loads(res.read())
            token_value = content.get("Token")
    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        token_value = "HTTPError"
        sys.exit()

    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        token_value = "Error"
        sys.exit()

    return token_value


# 板情報を取得する関数
def get_board(token, stock_code):
    url = f"http://localhost:{_host}/kabusapi/board/{stock_code}@1"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    current_price = trading_volume = symbol_name = None
    high_price = low_price = current_price_time = None

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            #     print(header)
            # print()
            content = json.loads(res.read())
            current_price = content.get("CurrentPrice")
            current_price_time = content.get("CurrentPriceTime")
            trading_volume = content.get("TradingVolume")
            symbol_name = content.get("SymbolName")
            change_previous_close_per = content.get("ChangePreviousClosePer")
            high_price = content.get("HighPrice")
            low_price = content.get("LowPrice")
            # pprint.pprint(content)
            # logger.debug(content)

    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        # content = json.loads(e.read())
        # pprint.pprint(content)
        sys.exit()
    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        sys.exit()

    return (
        current_price,
        trading_volume,
        symbol_name,
        change_previous_close_per,
        high_price,
        low_price,
        current_price_time,
    )


# 信用余力を取得する関数
def get_marginbalance(token, symbol=None):
    if symbol == None:
        url = f"http://localhost:{_host}/kabusapi/wallet/margin"

    else:
        url = f"http://localhost:{_host}/kabusapi/wallet/margin/{symbol}"

    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    wallet = None

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            #     print(header)
            # print()
            content = json.loads(res.read())
            wallet = content.get("MarginAccountWallet")
            # pprint.pprint(content)
            logger.debug(content)

    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        # content = json.loads(e.read())
        # pprint.pprint(content)
        sys.exit()
    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        sys.exit()

    return wallet


# ポジションを確認する関数
def get_position(token, product=0):
    url = f"http://localhost:{_host}/kabusapi/positions?product={product}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            #     print(header)
            # print()
            positions = json.loads(res.read())
            # pprint.pprint(positions)
            # logger.debug(positions)

    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        # content = json.loads(e.read())
        # pprint.pprint(content)
        sys.exit()
    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        sys.exit()

    data = []
    for position in positions:
        if position["Side"] == "2":
            side = "買"
        elif position["Side"] == "1":
            side = "売"
        try:
            typeid = position["MarginTradeType"]
            ordertype = "信用"
        except:
            typeid = -1
            ordertype = "現物"
        data.append(
            [
                ordertype,
                typeid,
                position["ExecutionID"],
                position["Symbol"],
                position["SymbolName"],
                side,
                position["Price"],
                position["LeavesQty"],
                position["CurrentPrice"],
                position["ProfitLoss"],
            ]
        )
    return pd.DataFrame(
        data,
        columns=[
            "注文種別",
            "信用注文タイプ",
            "ポジションID",
            "コード",
            "銘柄",
            "売買",
            "注文価格",
            "注文数",
            "現在価格",
            "損益",
        ],
    )


# 注文一覧を取得する関数
def get_order(token, order_type=0):
    url = f"http://localhost:{_host}/kabusapi/orders?product={order_type}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            #     print(header)
            # print()
            orders = json.loads(res.read())
            # orders = json.loads(res.text)
            # pprint.pprint(orders)
            # logger.debug(orders)

    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        # content = json.loads(e.read())
        # pprint.pprint(content)
        sys.exit()
    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        sys.exit()

    data = []

    for order in orders:
        state = order["State"]
        if state >= 4:  # 1,2,3: 待機,処理中,処理済
            continue
        price = order["Price"]
        if price == 0.0:
            price = "成行  "
        side = order["Side"]

        if side == "2":
            side = "買"
        elif side == "1":
            side = "売"

        current_price = get_board(token, order["Symbol"])

        if current_price == None:
            current_price = "---"

        data.append(
            [
                order["ID"],
                order["Symbol"],
                order["SymbolName"],
                price,
                side,
                order["OrderQty"],
                current_price,
                order["ExpireDay"],
            ]
        )

    return pd.DataFrame(data, columns=["注文ID", "コード", "銘柄", "注文価格", "売買", "注文数", "現在価格", "期限"])


# 信用取引の注文を発注する関数
def send_order_margin(token, symbol, side, qty, price, ordertype=20):
    if side == "buy":
        side = "2"
    elif side == "sell":
        side = "1"

    if int(ordertype) == 10:  # 成行注文の場合は価格が0でないとエラーになるため
        price = 0
    obj = {
        "Password": trading_pass,
        "Symbol": str(symbol),  # 銘柄コード
        "Exchange": 1,  # 1が「東証」
        "SecurityType": 1,  # 1が「株式」
        "Side": side,  # 1が「売り」、2が「買い」
        "CashMargin": 2,  # 1が「現物」 2が「信用」
        "MarginTradeType": 3,  # 1が「制度信用」2が「長期」3が「デイトレ」
        "DelivType": 0,
        "AccountType": 4,  # 口座の種類　2が「一般」4が「特定」
        "Qty": int(qty),
        "FrontOrderType": ordertype,
        "Price": price,
        "ExpireDay": 0,  # 0が「本日」
    }
    # print(obj)
    json_data = json.dumps(obj).encode("utf-8")
    url = f"http://localhost:{_host}/kabusapi/sendorder"
    req = urllib.request.Request(url, json_data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            # print(header)
            content = json.loads(res.read())
            logger.info(content)
            return content
    except urllib.error.HTTPError as e:
        # print(e)
        logger.exception("API Error.")
        content = json.loads(e.read())
        # pprint.pprint(content)
        sys.exit()
    except Exception as e:
        # print(e)
        logger.exception("API Error.")
        sys.exit()


# 信用取引のポジションを返済する関数
def send_order_close_margin(token, order_id, order_type, price, expire):
    position_data = get_position(token, 2)  # 「2」が信用

    for index, row in position_data.iterrows():
        if row["ポジションID"] == order_id:
            qty = row["注文数"]

            if order_type == 10:
                price = 0
            if row["売買"] == "買":
                side = "1"
            elif row["売買"] == "売":
                side = "2"
            # margintype = row["信用注文タイプ"]
            margintype = 3  # 1が「制度信用」2が「長期」3が「デイトレ」
            symbol = row["コード"]
            obj = {
                "Password": trading_pass,
                "Symbol": str(symbol),  # 銘柄コード
                "Exchange": 1,  # 1が「東証」
                "SecurityType": 1,  # 1が「株式」
                "FrontOrderType": order_type,  # 20が指値、10が成り行き int型
                "TimeInForce": 0,
                "Side": side,
                "CashMargin": 3,  # 1が「現物」 2が「信用新規」 3が「信用返済」
                "MarginTradeType": int(margintype),
                "DelivType": 2,
                "FundType": 11,
                "AccountType": 4,  # 口座の種類　4が「特定」
                "Qty": int(qty),
                "Price": int(price),
                "ExpireDay": expire,
                "ClosePositions": [{"HoldID": order_id, "Qty": qty}],
            }
            # print(obj)
            json_data = json.dumps(obj).encode("utf-8")
            url = f"http://localhost:{_host}/kabusapi/sendorder"
            req = urllib.request.Request(url, json_data, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("X-API-KEY", token)

            try:
                with urllib.request.urlopen(req) as res:
                    # print(res.status, res.reason)
                    # for header in res.getheaders():
                    #     print(header)
                    content = json.loads(res.read())
                    logger.info(content)
                    return content
            except urllib.error.HTTPError as e:
                # print(e)
                logger.exception("API Error.")
                # content = json.loads(e.read())
                # pprint.pprint(content)
                sys.exit()
            except Exception as e:
                # print(e)
                logger.exception("API Error.")
                sys.exit()


# 指定銘柄の全てのデイトレ信用ポジションを決済する関数
def all_close_margin(token, stock_code, order_type, price):
    position_data = get_position(token, 2)  # 「2」が信用

    for index, row in position_data.iterrows():
        if stock_code == row["コード"] and 3 == row["信用注文タイプ"]:
            qty = row["注文数"]
            order_id = row["ポジションID"]

            if qty != 0:
                send_order_close_margin(token, order_id, order_type, price, 0)
                time.sleep(1)


# 注文を取り消す関数
def cancel_order(token, id_):
    url = f"http://localhost:{_host}/kabusapi/cancelorder"
    obj = {"Password": trading_pass, "OrderId": id_}
    json_data = json.dumps(obj).encode("utf-8")
    req = urllib.request.Request(url, json_data, method="PUT")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", token)

    try:
        with urllib.request.urlopen(req) as res:
            # print(res.status, res.reason)
            # for header in res.getheaders():
            #     print(header)
            content = json.loads(res.read())
        return content

    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        logger.exception("API Error.")
        sys.exit()
    except Exception as e:
        print(e)
        logger.exception("API Error.")
        sys.exit()


# 指定銘柄の全てのデイトレ注文を取り消す関数
def all_cancel_order(token, stock_code):
    position_data = get_order(token, 2)  # 「2」が信用

    for index, row in position_data.iterrows():
        # logger.info(row)
        if stock_code == row["コード"]:
            order_id = row["注文ID"]
            cancel_order(token, order_id)
            time.sleep(1)


# 買い注文があるかどうか判定する関数
def is_buy_order(token, stock_code):
    position_data = get_order(token, 2)  # 「2」が信用

    for index, row in position_data.iterrows():
        if stock_code == row["コード"]:
            sell_buy = row["売買"]
            if sell_buy == "買":
                return True

    return False


# 売り注文があるかどうか判定する関数
def is_sell_order(token, stock_code):
    position_data = get_order(token, 2)  # 「2」が信用

    for index, row in position_data.iterrows():
        if stock_code == row["コード"]:
            sell_buy = row["売買"]
            if sell_buy == "売":
                return True

    return False
