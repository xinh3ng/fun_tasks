#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Procedure:
    Invoke virtual env (Python 3.6)
    $ python train_mammo_model.py --dataset_name=mnist --model_name=cnn --optimizer=adam --loss=categorical_crossentropy
"""
from pdb import set_trace as debug
import datetime
import locale
import urllib2
from BeautifulSoup import BeautifulSoup

import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

from pydsutils.generic import create_logger
logger = create_logger('scrape_and_email')

web_charset = "utf-8"
mail_charset = "ISO-2022-JP"

targeturl = "http://hogehoge.com/" # Target URL for scraping
targetclass = "h1" # Target element for scraping

from_address = "hogehoge@gmail.com" # Sender address (Gmail address)
from_password = "gmailpassword" # Sender server password (Gmail password)
to_address   = "fuga@fuga.com" # Recipient address

statusOK = u"Found / "
statusNG = u"Not Found"

def scraping(url):
    try:
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)
        target = soup.find(targetclass).renderContents()
        if len(target) == 0:
            return statusNG
        else:
            return statusOK + target.decode(web_charset)
    except:
        return statusNG

def create_message(from_addr, to_addr, subject, body, encoding):
    msg = MIMEText(body, 'plain', encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header(subject, encoding)
    msg["Date"] = formatdate(localtime=True)
    return msg

def sendmail(subject, text):
    msg = create_message(from_address, to_address, subject, text, mail_charset)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(from_address, from_password)
    s.sendmail(from_address, to_address, msg.as_string())
    s.close()


if __name__ == '__main__':
    d = datetime.datetime.today()
    time = d.strftime("%Y-%m-%d %H:%M:%S")
    mailsubject = u"Page Scraping // " + time
    mailmessage = scraping(targeturl)
    sendmail(mailsubject, mailmessage)
