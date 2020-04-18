'''Unit tests for Email worker tasks'''
# pylint: disable=no-member

from unittest import mock

import pytest

from harbor.domain.email import EmailMsg, EmailSecurity
from harbor.helpers.settings import get_settings
from harbor.worker.tasks import email


def test_get_address():
    '''Should return an Address object'''
    address = email.get_address('TestUser', 'user@kh.test')
    assert address.display_name == 'TestUser'
    assert address.username == 'user'
    assert address.domain == 'kh.test'


@pytest.fixture(name='msg')
def fixture_msg():
    '''Returns an EmailMsg model'''
    return EmailMsg(
        to_name='TestUser',
        to_email='user@kh.test',
        subject='test-subject',
        text='test-text-content',
        html='test-html-content',
    )


def assert_email_send(args):
    '''Helper to assert the email.send mock'''
    # Get settings
    settings = get_settings()

    # Assert results
    smtp_msg = args[0]
    assert smtp_msg['Subject'] == 'test-subject'
    assert smtp_msg['From'] == f'{settings.EMAIL_FROM.name} <{settings.EMAIL_FROM.email}>'
    assert smtp_msg['To'] == 'TestUser <user@kh.test>'


@pytest.mark.parametrize('with_login,username,password', [
    (False, '', ''),
    (True, 'test-username', 'test-password'),
])
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP_SSL')
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP')
def test_send_mail_unsecure(smtp, smtp_ssl, with_login, username, password, msg, monkeypatch):
    '''Should send a mail over unsecure SMTP'''
    # Mock ENV settings
    monkeypatch.setenv("EMAIL_USERNAME", username)
    monkeypatch.setenv("EMAIL_PASSWORD", password)
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.UNSECURE)
    get_settings.cache_clear()
    settings = get_settings()

    # Create mocks
    mock_smtp = mock.MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp
    smtp.return_value = mock_smtp

    # Call task
    email.send_mail(msg.dict())

    # Assert results
    smtp.assert_called_with(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT)
    smtp_ssl.assert_not_called()
    mock_smtp.starttls.assert_not_called()
    if with_login:
        mock_smtp.login.assert_called_with(username, password)
    else:
        mock_smtp.login.assert_not_called()
    args, _ = mock_smtp.send_message.call_args
    assert_email_send(args)


@pytest.mark.parametrize('with_login,username,password', [
    (False, '', ''),
    (True, 'test-username', 'test-password'),
])
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP_SSL')
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP')
def test_send_mail_tls_ssl(smtp, smtp_ssl, with_login, username, password, msg, monkeypatch):
    '''Should send a mail over SMTP secured with TLS/SSL'''
    # Mock ENV settings
    monkeypatch.setenv("EMAIL_USERNAME", username)
    monkeypatch.setenv("EMAIL_PASSWORD", password)
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.TLS_SSL)
    get_settings.cache_clear()
    settings = get_settings()

    # Create mocks
    mock_smtp = mock.MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp
    smtp_ssl.return_value = mock_smtp

    # Call task
    email.send_mail(msg.dict())

    # Assert results
    smtp_ssl.assert_called_with(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT)
    smtp.assert_not_called()
    mock_smtp.starttls.assert_not_called()
    if with_login:
        mock_smtp.login.assert_called_with(username, password)
    else:
        mock_smtp.login.assert_not_called()
    args, _ = mock_smtp.send_message.call_args
    assert_email_send(args)


@pytest.mark.parametrize('with_login,username,password', [
    (False, '', ''),
    (True, 'test-username', 'test-password'),
])
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP_SSL')
@mock.patch('harbor.worker.tasks.email.smtplib.SMTP')
def test_send_mail_starttls(smtp, smtp_ssl, with_login, username, password, msg, monkeypatch):
    '''Should send a mail over SMTP secured with STARTTLS'''
    # Mock ENV settings
    monkeypatch.setenv("EMAIL_USERNAME", username)
    monkeypatch.setenv("EMAIL_PASSWORD", password)
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.STARTTLS)
    get_settings.cache_clear()
    settings = get_settings()

    # Create mocks
    mock_smtp = mock.MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp
    smtp.return_value = mock_smtp

    # Call task
    email.send_mail(msg.dict())

    # Assert results
    smtp.assert_called_with(settings.EMAIL_HOSTNAME, settings.EMAIL_PORT)
    smtp_ssl.assert_not_called()
    mock_smtp.starttls.assert_called_with()
    if with_login:
        mock_smtp.login.assert_called_with(username, password)
    else:
        mock_smtp.login.assert_not_called()
    args, _ = mock_smtp.send_message.call_args
    assert_email_send(args)
