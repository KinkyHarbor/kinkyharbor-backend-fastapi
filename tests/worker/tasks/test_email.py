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
        to_name='test-User',
        to_email='user@kh.test',
        subject='test-subject',
        text='test-text-content',
        html='test-html-content',
    )


def assert_email_send(args, kwargs):
    '''Helper to assert the email.send mock'''
    # Get settings
    settings = get_settings()

    # Assert results
    smtp_msg = args[0]
    assert smtp_msg['Subject'] == 'test-subject'
    assert smtp_msg['From'] == f'{settings.EMAIL_FROM.name} <{settings.EMAIL_FROM.email}>'
    assert smtp_msg['To'] == 'TestUser <user@kh.test>'
    assert kwargs['hostname'] == settings.EMAIL_HOSTNAME
    assert kwargs['port'] == settings.EMAIL_PORT
    assert kwargs['username'] == settings.EMAIL_USERNAME
    assert kwargs['password'] == settings.EMAIL_PASSWORD.get_secret_value()


@mock.patch('harbor.helpers.email.aiosmtplib.send')
async def test_send_mail_unsecure(send, msg, monkeypatch):
    '''Should send a mail over unsecure SMTP'''
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.UNSECURE)
    get_settings.cache_clear()
    await email.send_mail(msg)
    args, kwargs = send.call_args
    assert 'use_tls' not in kwargs or not kwargs['use_tls']
    assert 'start_tls' not in kwargs or not kwargs['start_tls']
    assert_email_send(args, kwargs)


@mock.patch('harbor.helpers.email.aiosmtplib.send')
async def test_send_mail_tls_ssl(send, msg, monkeypatch):
    '''Should send a mail over SMTP secured with TLS/SSL'''
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.TLS_SSL)
    get_settings.cache_clear()
    await email.send_mail(msg)
    args, kwargs = send.call_args
    assert 'use_tls' in kwargs and kwargs['use_tls'] is True
    assert 'start_tls' not in kwargs or not kwargs['start_tls']
    assert_email_send(args, kwargs)


@mock.patch('harbor.helpers.email.aiosmtplib.send')
async def test_send_mail_starttls(send, msg, monkeypatch):
    '''Should send a mail over SMTP secured with STARTTLS'''
    monkeypatch.setenv("EMAIL_SECURITY", EmailSecurity.STARTTLS)
    get_settings.cache_clear()
    await email.send_mail(msg)
    args, kwargs = send.call_args
    assert 'use_tls' not in kwargs or not kwargs['use_tls']
    assert 'start_tls' in kwargs and kwargs['start_tls'] is True
    assert_email_send(args, kwargs)
