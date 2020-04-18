'''This module contains email tasks for Celery'''
# pylint: disable=no-member

import smtplib
from email.headerregistry import Address
from email.message import EmailMessage
from typing import Dict

from harbor.domain.email import EmailMsg, EmailSecurity
from harbor.helpers.settings import get_settings
from harbor.worker.app import app


def get_address(name: str, email: str) -> Address:
    '''Returns an Address based on recipient name and mail address'''
    email_parts = email.split('@')
    return Address(name, email_parts[0], email_parts[1])


@app.task
def send_mail(msg_dict: Dict):
    '''Sends a mail

    Arguments
        msg: EmailMsg formatted as Dict
    '''
    # Parse message
    msg = EmailMsg(**msg_dict)

    # Get settings
    settings = get_settings()

    # Build message
    smtp_msg = EmailMessage()
    smtp_msg['Subject'] = msg.subject
    smtp_msg['From'] = get_address(settings.EMAIL_FROM.name,
                                   settings.EMAIL_FROM.email)
    smtp_msg['To'] = get_address(msg.to_name, msg.to_email)
    smtp_msg.set_content(msg.text)
    smtp_msg.add_alternative(msg.html, subtype='html')

    # Use SMTP_SSL class if TLS/SSL is enabled
    if settings.EMAIL_SECURITY == EmailSecurity.TLS_SSL:
        SMTP = smtplib.SMTP_SSL
    else:
        SMTP = smtplib.SMTP

    with SMTP(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT) as smtp:
        # Start STARTTLS if enabled
        if settings.EMAIL_SECURITY == EmailSecurity.STARTTLS:
            smtp.starttls()
            smtp.ehlo()

        # Login if required
        username = settings.EMAIL_USERNAME
        password = settings.EMAIL_PASSWORD.get_secret_value()
        if username or password:
            smtp.login(username, password)

        # Send message
        smtp.send_message(smtp_msg)
