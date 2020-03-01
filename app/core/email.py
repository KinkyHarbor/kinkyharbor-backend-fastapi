import smtplib
from email.message import EmailMessage
from email.headerregistry import Address

from core import settings


def get_address(name: str, email: str):
    email_parts = email.split('@')
    return Address(name, email_parts[0], email_parts[1])


def send_mail(to: Address, subject: str, content_text: str, content_html: str = None):
    # Build message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = get_address(settings.EMAIL_FROM_NAME,
                              settings.EMAIL_FROM_ADDRESS)
    msg['To'] = to
    msg.set_content(content_text)
    if content_html:
        msg.add_alternative(content_html, subtype='html')

    # Send message
    with smtplib.SMTP(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT) as s:
        try:
            s.starttls()
            s.ehlo()
        except smtplib.SMTPNotSupportedError:
            pass
        if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
            s.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        s.send_message(msg)


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
