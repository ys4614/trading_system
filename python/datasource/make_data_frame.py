import talib as ta


def update_df(
    df,
    pattern,
):
    close = df["Adj Close"]

    # 過去5日、25日、50日の移動平均を算出する為に定義
    span01 = 5
    span02 = 25
    span03 = 50

    # MACD、シグナル、ヒストグラムを算出
    # ta.MACD(終値, 短期移動平均, 長期移動平均, MACDシグナル)
    fast = 12
    slow = 26
    signal = 9

    # match pattern:
    #     case "15s" | "30s" | "1m":
    #         span01 = 3
    #         span02 = 10
    #         span03 = 20

    #         fast = 6
    #         slow = 19
    #         signal = 4

    #     case "5m":
    #         span01 = 4
    #         span02 = 12
    #         span03 = 24

    #         fast = 9
    #         slow = 24
    #         signal = 6

    # 移動平均を算出
    # smaは単純移動平均の略称
    df["sma01"] = close.rolling(window=span01).mean()
    df["sma02"] = close.rolling(window=span02).mean()
    df["sma03"] = close.rolling(window=span03).mean()

    # MACD、シグナル、ヒストグラムを算出
    # ta.MACD(終値, 短期移動平均, 長期移動平均, MACDシグナル)
    df["macd"], df["macdsignal"], df["macdhist"] = ta.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    df.tail()

    # df['RSI'] = ta.RSI(終値, RSIを作成する期間)
    df["RSI"] = ta.RSI(close, timeperiod=span02)

    # matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (デフォルト=SMA)

    # 上のボリンジャーバンド, 移動平均, 下のボリンジャーバンド = ta.BBANDS(調整済み終値, 日経平均日数, 上のラインの標準偏差, 下のラインの標準偏差, 移動平均の計算方法)インの標準偏差, ○○移動平均)
    df["upper"], df["middle"], df["lower"] = ta.BBANDS(close, timeperiod=span02, nbdevup=2, nbdevdn=2, matype=0)

    return df
