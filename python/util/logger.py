import logging
import logging.handlers
import os

logger = logging.getLogger("trading_system").getChild(__name__)


# log出力
def output_log(logic_name, stock_code, s):
    logger.info(stock_code + "," + s)


class TlsSMTPHandler(logging.handlers.SMTPHandler):
    """
    loggingをGmailで送信させるために、SMTPHandlerをオーバーライドしてTLSに対応させる。
    参考: https://gist.github.com/Agasper/8ef727892f7d8d63e0ac
    """

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib

            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ",".join(self.toaddrs),
                self.getSubject(record),
                formatdate(),
                msg,
            )
            if self.username:
                smtp.ehlo()  # for tls add this line
                smtp.starttls()  # for tls add this line
                smtp.ehlo()  # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def set_logger(module_name):
    """共通のロガーを定義する

    Args:
        module_name (str)

    Returns:
        logger
    """
    logger = logging.getLogger(module_name)
    logger.handlers.clear()

    streamHandler = logging.StreamHandler()
    fileHandler = logging.handlers.RotatingFileHandler("./trade.log", maxBytes=10000000, backupCount=5)

    from_gmail = os.getenv("GMAIL")
    app_password = os.getenv("GMAIL_KEY")
    to_mail = os.getenv("GMAIL")

    emailHandler = TlsSMTPHandler(
        mailhost=("smtp.gmail.com", 587),
        fromaddr=from_gmail,
        toaddrs=[to_mail],
        subject="{Urgent} CHECK LOGS",
        credentials=(from_gmail, app_password),
    )

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s | %(funcName)s | %(lineno)s) %(message)s")

    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    emailHandler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    streamHandler.setLevel(logging.DEBUG)
    fileHandler.setLevel(logging.DEBUG)
    emailHandler.setLevel(logging.WARNING)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    logger.addHandler(emailHandler)

    return logger
