import winsound

from util import save_file

import logging

logger = logging.getLogger("trading_system").getChild(__name__)


# 信用買い要求
def transaction_execute_buy_in(logic_name, stock_code, symbol_name, value, log_message):
    save_file.result_output_csv(logic_name, stock_code, symbol_name, "Buy", "In", value)
    logger.output_log(logic_name, stock_code, log_message)
    # beepWindpwsPc()


# 空売り要求
def transaction_execute_sell_in(logic_name, stock_code, symbol_name, value, log_message):
    save_file.result_output_csv(logic_name, stock_code, symbol_name, "Sell", "In", value)
    logger.output_log(logic_name, stock_code, log_message)
    # beepWindpwsPc()


# 信用買い返済
def transaction_execute_buy_out(logic_name, stock_code, symbol_name, value, log_message, diff):
    save_file.result_output_csv(logic_name, stock_code, symbol_name, "Buy", "Out", value, diff)
    logger.output_log(logic_name, stock_code, log_message)
    # beepWindpwsPc()


# 空売り返済
def transaction_execute_sell_out(logic_name, stock_code, symbol_name, value, log_message, diff):
    save_file.result_output_csv(logic_name, stock_code, symbol_name, "Sell", "Out", value, diff)
    logger.output_log(logic_name, stock_code, log_message)
    # beepWindpwsPc()


# PCのビープ音
def beepWindpwsPc():
    frequency = 500
    duration = 800
    winsound.Beep(frequency, duration)
