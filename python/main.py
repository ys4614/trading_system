import os
import datetime
import time
import concurrent.futures
import shutil
import subprocess
import pyautogui
from pathlib import Path

from util import logger

logger = logger.set_logger("trading_system")

from util import send_mail
from util import trading_time
from util import update_index
from datasource import trade_api
from datasource import collect_trade_data

import global_value as g
import main_logic

# kabu STATION password
value = os.getenv("ENV_KABU_PASS")
# value = os.getenv["ENV_KABU_PASS_TEST"]


def func():
    # 前日までの株価データを取得する
    for i, j, k in g.code_list:
        collect_trade_data.func(i, k)

    token = trade_api.generate_token(value)
    # logger.info(f"token:{token}")

    cash = trade_api.get_marginbalance(token)
    logger.info(f"信用残高：{cash}円\n---------------")

    position_data = trade_api.get_position(token)
    logger.info(f"ポジション：\n{position_data}\n---------------")

    future_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 日経、マザーズの前日比を更新
        future = executor.submit(update_index.update_index, token=token)
        future_list.append(future)

        for i, j, k in g.code_list:
            future = executor.submit(main_logic.trader_func, token=token, stock_code=i, qty=j)
            future_list.append(future)

            # API制限回避のためウェイト。秒10回以上でエラーになる。
            time.sleep(0.5)

    logger.info("End")


def start_app():
    user_name = os.getlogin()
    p = subprocess.Popen(
        rf"C:\Users\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com\kabuステーション.appref-ms",
        shell=True,
    )

    time.sleep(10)
    pyautogui.write(value, interval=0.2)
    time.sleep(2)
    pyautogui.press("enter")
    time.sleep(10)


def finish_app():
    pyautogui.hotkey("alt", "space")
    time.sleep(1)
    pyautogui.press("c")
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(10)


if __name__ == "__main__":
    # フォルダ作成
    path = Path("./python/logs")
    path.mkdir(parents=True, exist_ok=True)
    path = Path("./python/data")
    path.mkdir(parents=True, exist_ok=True)
    path = Path("./python/backup")
    path.mkdir(parents=True, exist_ok=True)

    func()

    # 取引時間内に終了した場合は、エラーメールを送信する
    if trading_time.finish_time() == False:
        send_mail.send_mail("＊要確認＊", "プログラムを終了しました。")

    today = datetime.date.today()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    src = current_directory + "/data"
    dst = current_directory + "/backup/" + str(today)
    shutil.copytree(src, dst)

    # アプリを自動起動して運用する場合に使用する。
    # while True:
    #     start_app()
    #     func()

    #     # 取引時間内の場合はエラーメール送信
    #     current_time = datetime.datetime.now().time()
    #     finish_time = datetime.time(15, 0, 0)
    #     if current_time < finish_time:
    #         finish_app()
    #         trade_util.send_mail("＊要確認＊", "プログラムを再起動しました。")
    #     else:
    #         finish_app()
    #         break
