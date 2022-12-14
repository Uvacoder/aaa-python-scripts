#!/usr/bin/python
import smtplib

sender = "from@fromdomain.com"
receivers = ["to@todomain.com"]

message = f"""From: From Person {sender}
To: To Person {receivers}
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
    smtpObj = smtplib.SMTP("localhost")
    smtpObj.sendmail(sender, receivers, message)
    print("succes send!")
except smtplib.SMTPException:
    print("Error: unable to send email")
