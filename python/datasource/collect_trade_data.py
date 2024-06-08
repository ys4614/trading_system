import os
import pandas as pd

import yfinance as yf
import global_value as g

from datasource import make_data_frame as mdf


def func(code, stock_code):
    # 直近、1日間の分間隔の株情報を取得する
    # periodでは、1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,maxを設定できる
    # intervalでは、1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3moを設定できる
    current_directory = os.path.dirname(os.path.abspath(__file__))
    prefilename = current_directory + "/data/" + code + "-"

    for i in g.data_pattern:
        filename = prefilename + i["pattern"] + ".csv"
        if os.path.exists(filename):
            print("対象のcsvファイルが存在しています")
            continue

        df = yf.download(tickers=stock_code, period=i["period"], interval=i["interval"])

        # 日付を昇順に並び替える
        df.sort_index(inplace=True)
        df.to_csv(filename)  # CSVファイルに株価データを保存
        df = pd.read_csv(filename)  # CSVファイルから株価データを呼び出し

        if i["interval"] == "1d":
            df = df.set_index("Date")  # データフレームを元の形に直す
        else:
            df = df.set_index("Datetime")  # データフレームを元の形に直す

        # MACD等の算出
        df = mdf.update_df(df, i["pattern"])

        # CSVファイルに株価データを保存
        df.to_csv(filename)


if __name__ == "__main__":
    for i, j, k in g.code_list:
        func(i, k)
