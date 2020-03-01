'''This module contains everything to prepare and send mails'''
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address

from core import settings
from models.email import EmailMsg


def get_address(name: str, email: str) -> Address:
    '''Returns an Address based on recipient name and mail address'''
    email_parts = email.split('@')
    return Address(name, email_parts[0], email_parts[1])


def send_mail(msg: EmailMsg):
    '''Sends an email'''
    # Build message
    smtp_msg = EmailMessage()
    smtp_msg['Subject'] = msg.subject
    smtp_msg['From'] = get_address(settings.EMAIL_FROM_NAME,
                                   settings.EMAIL_FROM_ADDRESS)
    smtp_msg['To'] = msg.recipient
    smtp_msg.set_content(msg.text)
    smtp_msg.add_alternative(msg.html, subtype='html')

    # Send message
    with smtplib.SMTP(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT) as s:
        try:
            s.starttls()
            s.ehlo()
        except smtplib.SMTPNotSupportedError:
            pass
        if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
            s.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        s.send_message(smtp_msg)


TEMPLATE_REGISTER_TEXT = """\
Welcome to Kinky Harbor!
Please verify your mail address by clicking {registration_link}
"""

TEMPLATE_REGISTER_HTML = """\
<html>
  <head></head>
  <body>
    <p>Welcome to Kinky Harbor!</p>
    <p>Please verify your mail address by clicking
        <a href="{registration_link}">{registration_link}</a>.
    </p>
  </body>
</html>
"""


def prepare_register_verification(recipient: Address, secret: str) -> EmailMsg:
    registration_link = f'{settings.FRONTEND_URL}/register/verify?token={secret}'
    msg = TEMPLATE_REGISTER_TEXT.format(
        registration_link=registration_link)
    msg_html = TEMPLATE_REGISTER_HTML.format(
        registration_link=registration_link)

    return EmailMsg(
        recipient=recipient,
        subject='Verify your Kinky Harbor account',
        text=msg,
        html=msg_html,
    )


TEMPLATE_REGISTER_EMAIL_EXISTS_TEXT = """\
There was an attempt to create a new account on Kinky Harbor with this mail adress.
In case you forgot your password, please request a reset at {reset_password_link}.
If you didn't try to register, safely ignore this message.
"""

TEMPLATE_REGISTER_EMAIL_EXISTS_HTML = """\
<html>
  <head></head>
  <body>
    <p>There was an attempt to create a new account on Kinky Harbor with this mail adress.</p>
    <p>In case you forgot your password, please request a reset at
        <a href="{reset_password_link}">{reset_password_link}</a>.
    </p>
    <p>If you didn't try to register, safely ignore this message.</p>
  </body>
</html>
"""


def prepare_register_email_exist(recipient: Address) -> EmailMsg:
    reset_password_link = f'{settings.FRONTEND_URL}/reset-password/'
    msg = TEMPLATE_REGISTER_EMAIL_EXISTS_TEXT.format(
        reset_password_link=reset_password_link)
    msg_html = TEMPLATE_REGISTER_EMAIL_EXISTS_HTML.format(
        reset_password_link=reset_password_link)

    return EmailMsg(
        recipient=recipient,
        subject='Registration attempt at Kinky Harbor',
        text=msg,
        html=msg_html,
    )
