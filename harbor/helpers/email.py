'''This module contains everything to prepare and send mails'''

from email.message import EmailMessage
from email.headerregistry import Address

import aiosmtplib

from harbor.domain.email import EmailMsg, EmailSecurity
from harbor.helpers import settings


def get_address(name: str, email: str) -> Address:
    '''Returns an Address based on recipient name and mail address'''
    email_parts = email.split('@')
    return Address(name, email_parts[0], email_parts[1])


async def send_mail(msg: EmailMsg):
    '''Sends an email'''
    # Build message
    # Build message
    smtp_msg = EmailMessage()
    smtp_msg['Subject'] = msg.subject
    smtp_msg['From'] = get_address(settings.EMAIL_FROM_NAME,
                                   settings.EMAIL_FROM_ADDRESS)
    smtp_msg['To'] = msg.recipient
    smtp_msg.set_content(msg.text)
    smtp_msg.add_alternative(msg.html, subtype='html')

    # Get security
    mail_sec = settings.EMAIL_SECURITY
    if mail_sec == EmailSecurity.TLS_SSL:
        sec_opts = {'use_tls': True}
    elif mail_sec == EmailSecurity.STARTTLS:
        sec_opts = {'start_tls': True}
    else:
        # Unsecure
        sec_opts = {}

    # Send mail
    await aiosmtplib.send(
        smtp_msg,
        hostname=settings.EMAIL_HOSTNAME,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_USERNAME,
        password=settings.EMAIL_PASSWORD,
        **sec_opts)


TEMPLATE_REGISTER_TEXT = """\
Welcome to Kinky Harbor!
Please verify your mail address by clicking {registration_link}

- Kinky Harbor crew -
"""

TEMPLATE_REGISTER_HTML = """\
<html>
  <head></head>
  <body>
    <p>Welcome to Kinky Harbor!</p>
    <p>Please verify your mail address by clicking
        <a href="{registration_link}">{registration_link}</a>.
    </p>
    <p>- Kinky Harbor crew -</p>
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

- Kinky Harbor crew -
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
    <p>- Kinky Harbor crew -</p>
  </body>
</html>
"""


def prepare_register_email_exist(recipient: Address) -> EmailMsg:
    reset_password_link = f'{settings.FRONTEND_URL}/login/request-reset/'
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


TEMPLATE_RESET_PASSWORD_TEXT = """\
A password reset has been requested for this mail address.
Please use following link to set a new password: {reset_password_link}.
If you didn't try to reset your password, safely ignore this message.

- Kinky Harbor crew -
"""

TEMPLATE_RESET_PASSWORD_HTML = """\
<html>
  <head></head>
  <body>
    <p>A password reset has been requested for this mail address.</p>
    <p>Please use following link to set a new password:
        <a href="{reset_password_link}">{reset_password_link}</a>.
    </p>
    <p>If you didn't try to reset your password, safely ignore this message.</p>
    <p>- Kinky Harbor crew -</p>
  </body>
</html>
"""


def prepare_reset_password(recipient: Address, user_id: str, token: str) -> EmailMsg:
    reset_password_link = f'{settings.FRONTEND_URL}/login/reset-password?user={user_id}&token={token}'
    msg = TEMPLATE_RESET_PASSWORD_TEXT.format(
        reset_password_link=reset_password_link)
    msg_html = TEMPLATE_RESET_PASSWORD_HTML.format(
        reset_password_link=reset_password_link)

    return EmailMsg(
        recipient=recipient,
        subject='Password reset for Kinky Harbor',
        text=msg,
        html=msg_html,
    )
