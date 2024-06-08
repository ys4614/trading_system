import datetime
import os


# csvに取引履歴を出力
def result_output_csv(logic_name, stock_code, symbol_name, bs, io, value, diff=""):
    d = datetime.date.today()
    current_time = datetime.datetime.now().time()
    t = current_time.strftime("%H:%M:%S")

    current_directory = os.path.dirname(os.path.abspath(__file__))
    filename = f"{current_directory}/logs/{d}_result_output_{logic_name}.csv"
    with open(filename, "a") as f:
        s = f"{stock_code},{symbol_name},{t},{bs},{io},{value},{diff}\n"
        f.write(s)

    # ビープ
    # beepWindpwsPc()


# csvに取引結果を出力
def report_output_csv(logic_name, report):
    d = datetime.date.today()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    filename = f"{current_directory}/logs/{d}_report_output_{logic_name}.csv"
    with open(filename, "a") as f:
        f.write(report)
