#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Procedure:
    Invoke virtual env (Python 3.6)
    $ python scrape_and_email.py
"""
from pdb import set_trace as debug
import os
import datetime
import json
from pathlib import Path

from  urllib.request import urlretrieve
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from pydsutils.generic import create_logger

logger = create_logger('scrape_and_email')
now = datetime.datetime.today()

email_subject_map = {
    'http://daily.awesomeport.cn': {
        'subject': u'好东西传送门 - daily - ' + now.strftime("%Y-%m-%d %H:%M:%S")
    }

}

def get_email_passwd(sender: str) -> str:
    """Retrieve email pass code
    
    pass code must be saved in JSON format: {email_address: passwd}
    Args:
        sender: Sender email 
    """
    secretfile = '{home}/cred/email_logins.json'.format(home=os.environ['HOME'])
    with open(secretfile) as f:
        data = json.load(f)
    assert sender in data.keys(), '{} pass code not found'.format(sender)
    return data[sender]


def gen_html_mesg(file):
    """Generate html content that can go as an email body
    """
    content = Path(file).read_text()
    message = MIMEText(content, 'html')
    return message


def scrape_url(url):
    """Scrape the give URL"""
    status = {
        'ok': 'Found',
        'ng': 'Not Found'
    }
    logger.info('Start scraping the website content...')
    tmp_html = '/tmp/web_content_to_html.html'
    try:
        urlretrieve(url, tmp_html)
    except:
        return MIMEText(status['ng'], 'plain')

    message = gen_html_mesg(tmp_html)
    logger.info('Successfully embedded the HTML as an email message...')
    return message


def create_email(subject, message, sender, recipients):
    msg = MIMEMultipart()  # create a message
    msg.add_header('From', sender)
    msg.add_header('To', recipients)
    msg.add_header('Subject', subject)
    msg.add_header('Date', formatdate(localtime=True))
    msg.attach(message)
    logger.info('Successfully created the entire email')
    return msg


def send_email(mime_mesg, sender, recipients):
    """Send out an email"""

    logger.info('Logging onto mail server...')
    sess = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    sess.set_debuglevel(False)  # set to True for verbose
    sess.ehlo()
    sess.starttls()
    sess.ehlo()
    sess.login(sender, get_email_passwd(sender))
    logger.info('Successfully logged on')

    sess.sendmail(sender, recipients, mime_mesg.as_string())
    sess.quit()
    logger.info('Successfully sent email and closed mail server')
    return


def main(target_url: str,
        sender: str = 'xin.heng@outlook.com',
        recipients: str = 'xin.heng@outlook.com') -> None:
    """
    Procedure is simple: create an email message -> log onto email account -> send the email
    Args:
        target_url: The website URL to be scraped
        sender: Sender email
        recipients: Recipients' emails
    """
    subject = email_subject_map[target_url]['subject']
    message = scrape_url(target_url)
    msg = create_email(subject, message, sender, recipients)
    send_email(msg, sender, recipients)
    return


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_url', default='http://daily.awesomeport.cn')

    args = parser.parse_args()
    main(**vars(args))
    logger.info("ALL DONE")
