import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# メール送信
def send_mail_base(gmail, password, mail, mailText, subject):
    charset = "iso-2022-jp"
    msg = MIMEText(mailText, "plain", charset)
    msg["Subject"] = Header(subject.encode(charset), charset)
    smtp_obj = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_obj.ehlo()
    smtp_obj.starttls()
    smtp_obj.login(gmail, password)
    smtp_obj.sendmail(gmail, mail, msg.as_string())
    smtp_obj.quit()


# メール送信自分用
def send_mail(summary, mailText):
    gmail = os.getenv("GMAIL")
    password = os.getenv("GMAIL_KEY")
    mail = os.getenv("GMAIL")
    # mail = os.getenv('YMAIL')
    mailText = mailText
    subject = summary
    send_mail_base(gmail, password, mail, mailText, subject)
