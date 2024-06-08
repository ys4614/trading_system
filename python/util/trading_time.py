import datetime


# 取引時間（アプリ起動時間）
trading_start_time_am = datetime.time(9, 0, 0)
trading_end_time_am = datetime.time(11, 30, 0)
trading_start_time_pm = datetime.time(12, 30, 0)
trading_end_time_pm = datetime.time(15, 00, 0)
trading_finish_time = datetime.time(14, 55, 0)


# 取引時間チェック
def trading_time():
    current_time = datetime.datetime.now().time()
    if (
        trading_start_time_am < current_time < trading_end_time_am
        or trading_start_time_pm < current_time < trading_finish_time
    ):
        return True
    else:
        return False


# 取引終了時間帯チェック
def before_finish_time():
    current_time = datetime.datetime.now().time()
    if trading_finish_time < current_time < trading_end_time_pm:
        return True
    else:
        return False


# 取引時間終了チェック
def finish_time():
    current_time = datetime.datetime.now().time()
    if current_time > trading_end_time_pm:
        return True
    else:
        return False


# 経過時間チェック
def check_elapsed_time(start_time, timeout):
    current_time = datetime.datetime.now()
    time_difference = current_time - start_time
    elapsed_seconds = time_difference.total_seconds()

    if elapsed_seconds >= timeout:
        return True
    else:
        return False
