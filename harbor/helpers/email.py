'''This module contains all email templates'''

from harbor.domain.email import EmailMsg
from harbor.helpers.settings import get_settings


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


def prepare_register_verification(to_name: str, to_email: str, secret: str) -> EmailMsg:
    '''Prepare mail with registration verification link'''
    # Get settings
    settings = get_settings()

    # Build message
    registration_link = f'{settings.FRONTEND_URL}/register/verify?token={secret}'
    msg = TEMPLATE_REGISTER_TEXT.format(
        registration_link=registration_link)
    msg_html = TEMPLATE_REGISTER_HTML.format(
        registration_link=registration_link)

    return EmailMsg(
        to_name=to_name,
        to_email=to_email,
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


def prepare_register_email_exist(to_name: str, to_email: str) -> EmailMsg:
    '''Prepare mail with link to request a password reset'''
    # Get settings
    settings = get_settings()

    # Build message
    reset_password_link = f'{settings.FRONTEND_URL}/login/request-reset/'
    msg = TEMPLATE_REGISTER_EMAIL_EXISTS_TEXT.format(
        reset_password_link=reset_password_link)
    msg_html = TEMPLATE_REGISTER_EMAIL_EXISTS_HTML.format(
        reset_password_link=reset_password_link)

    return EmailMsg(
        to_name=to_name,
        to_email=to_email,
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


def prepare_reset_password(to_name: str, to_email: str, user_id: str, token: str) -> EmailMsg:
    '''Prepare mail with link to reset your password'''
    # Get settings
    settings = get_settings()

    # Build message
    link = f'{settings.FRONTEND_URL}/login/reset-password?user={user_id}&token={token}'
    msg = TEMPLATE_RESET_PASSWORD_TEXT.format(reset_password_link=link)
    msg_html = TEMPLATE_RESET_PASSWORD_HTML.format(reset_password_link=link)

    return EmailMsg(
        to_name=to_name,
        to_email=to_email,
        subject='Password reset for Kinky Harbor',
        text=msg,
        html=msg_html,
    )
