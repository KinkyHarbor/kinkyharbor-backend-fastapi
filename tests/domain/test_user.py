'''Unit tests for user domain'''

from harbor.domain.user import BaseUser


def test_success_set_username():
    '''Username should be filled with lowercase display name'''
    user = BaseUser(
        display_name='TestUser123',
    )
    assert user.username == 'testuser123'


def test_success_overwrite_username():
    '''Username should be filled with lowercase display name'''
    user = BaseUser(
        display_name='TestUser123',
        username='test-user'
    )
    assert user.username == 'testuser123'
