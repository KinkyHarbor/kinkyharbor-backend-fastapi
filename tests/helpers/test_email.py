'''Unit tests for Email helpers'''

from unittest import mock

import pytest

from harbor.domain.email import EmailMsg, EmailSecurity
from harbor.helpers import email
from harbor.helpers.settings import Settings, get_settings


def test_get_address():
    '''Should return an Address object'''
    address = email.get_address('TestUser', 'user@kh.test')
    assert address.display_name == 'TestUser'
    assert address.username == 'user'
    assert address.domain == 'kh.test'


@pytest.fixture(name='recipient')
def fixture_recipient():
    '''Returns a mail recipient'''
    return email.get_address('TestUser', 'user@kh.test')


@pytest.fixture(name='msg')
def fixture_msg(recipient):
    '''Returns an EmailMsg model'''
    return EmailMsg(
        recipient=recipient,
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
    assert kwargs['password'] == settings.EMAIL_PASSWORD


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


def test_prepare_register_verification(recipient):
    '''Should return a formatted mail'''
    msg = email.prepare_register_verification(recipient, 'test-secret')
    assert msg.recipient == recipient
    assert 'verify' in msg.subject.lower()
    assert 'account' in msg.subject.lower()
    assert 'test-secret' in msg.text
    assert '{' not in msg.text
    assert 'test-secret' in msg.html
    assert '{' not in msg.html


def test_prepare_register_email_exist(recipient):
    '''Should return a formatted mail'''
    msg = email.prepare_register_email_exist(recipient)
    assert msg.recipient == recipient
    assert '{' not in msg.text
    assert '{' not in msg.html


def test_prepare_reset_password(recipient):
    '''Should return a formatted mail'''
    msg = email.prepare_reset_password(
        recipient, 'test-user-id', 'test-secret')
    assert msg.recipient == recipient
    assert 'reset' in msg.subject.lower()
    assert 'test-user-id' in msg.text
    assert 'test-secret' in msg.text
    assert '{' not in msg.text
    assert 'test-user-id' in msg.html
    assert 'test-secret' in msg.html
    assert '{' not in msg.html
