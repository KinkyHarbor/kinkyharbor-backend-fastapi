'''Unit tests for Email helpers'''

from harbor.helpers import email


def test_prepare_register_verification():
    '''Should return a formatted mail'''
    msg = email.prepare_register_verification(to_name='test-user',
                                              to_email='user@kh.test',
                                              secret='test-secret')
    assert msg.to_name == 'test-user'
    assert msg.to_email == 'user@kh.test'
    assert 'verify' in msg.subject.lower()
    assert 'account' in msg.subject.lower()
    assert 'test-secret' in msg.text
    assert '{' not in msg.text
    assert 'test-secret' in msg.html
    assert '{' not in msg.html


def test_prepare_register_email_exist():
    '''Should return a formatted mail'''
    msg = email.prepare_register_email_exist(to_name='test-user',
                                             to_email='user@kh.test')
    assert msg.to_name == 'test-user'
    assert msg.to_email == 'user@kh.test'
    assert '{' not in msg.text
    assert '{' not in msg.html


def test_prepare_reset_password():
    '''Should return a formatted mail'''
    msg = email.prepare_reset_password(to_name='test-user',
                                       to_email='user@kh.test',
                                       user_id='test-user-id',
                                       token='test-secret')
    assert msg.to_name == 'test-user'
    assert msg.to_email == 'user@kh.test'
    assert 'reset' in msg.subject.lower()
    assert 'test-user-id' in msg.text
    assert 'test-secret' in msg.text
    assert '{' not in msg.text
    assert 'test-user-id' in msg.html
    assert 'test-secret' in msg.html
    assert '{' not in msg.html
