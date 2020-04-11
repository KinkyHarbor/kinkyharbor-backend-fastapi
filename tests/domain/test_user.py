'''Unit tests for user domain'''

import pytest

from harbor.domain.user import BaseUser, User, UserRelation


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


@pytest.mark.parametrize('user_id,friends,expected', [
    ('507f1f77bcf86cd799439011',
     [],
     UserRelation.SELF),
    ('507f1f77bcf86cd799439022',
     ['507f1f77bcf86cd799439022'],
     UserRelation.FRIEND),
    ('507f1f77bcf86cd799439022',
     [],
     UserRelation.STRANGER),
    ('507f1f77bcf86cd799439022',
     ['507f1f77bcf86cd799439033'],
     UserRelation.STRANGER),
])
def test_success_get_relation(user_id, friends, expected):
    '''Should return relation between user and provided user'''
    user = User(
        id='507f1f77bcf86cd799439011',
        display_name="TestUser",
        friends=friends,
    )
    result = user.get_relation(user_id)
    assert result == expected


def test_fail_get_relation():
    '''Should return a ValueError if user ID is not set'''
    user = User(display_name="TestUser")
    with pytest.raises(ValueError):
        user.get_relation('507f1f77bcf86cd799439011')
