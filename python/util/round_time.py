from datetime import datetime, timedelta


def round_to_nearest_seconds(input_time, seconds):
    # 秒数をsecondsの倍数に丸める
    rounded_seconds = (input_time.second // seconds) * seconds
    # マイクロ秒を0に設定
    rounded_time = input_time.replace(second=rounded_seconds, microsecond=0)
    return rounded_time


def round_to_nearest_minutes(input_time, minutes):
    # 分数を1の倍数に丸める
    rounded_minutes = (input_time.minute // minutes) * minutes
    # 秒とマイクロ秒を0に設定
    rounded_time = input_time.replace(minute=rounded_minutes, second=0, microsecond=0)
    return rounded_time
