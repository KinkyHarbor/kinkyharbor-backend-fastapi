'''Unit tests for User Profile Get usecase'''

from unittest import mock

import pytest

from harbor.domain.user import User, FRIEND_FIELDS, STRANGER_FIELDS
from harbor.repository.base import UserRepo
from harbor.use_cases.user import profile_get as uc_get

# =======================================
# =               HELPERS               =
# =======================================


def get_user_self():
    '''Returns own user'''
    return User(
        id='507f1f77bcf86cd799439011',
        display_name='TestUser',
    )


def get_uc_res_self(user_self):
    '''Returns a usecase response for own user'''
    return uc_get.GetProfileResponse(
        user=user_self,
        exposed_fields=list(user_self.fields.keys()),
        is_self=True,
        is_friend=False,
    )


def get_user_friend():
    '''Returns a friend's user'''
    return User(
        id='507f1f77bcf86cd799439022',
        display_name='TestUser2',
        friends=['507f1f77bcf86cd799439011'],
    )


def get_uc_res_friend(user_friend):
    '''Returns a usecase response for a friend'''
    return uc_get.GetProfileResponse(
        user=user_friend.copy(include=FRIEND_FIELDS),
        exposed_fields=FRIEND_FIELDS,
        is_self=False,
        is_friend=True,
    )


def get_user_stranger():
    '''Returns a strangers's user'''
    return User(
        id='507f1f77bcf86cd799439033',
        display_name='TestUser3',
    )


def get_uc_res_stranger(user_stranger):
    '''Returns a usecase response a stranger'''
    return uc_get.GetProfileResponse(
        user=user_stranger.copy(include=STRANGER_FIELDS),
        exposed_fields=STRANGER_FIELDS,
        is_self=False,
        is_friend=False,
    )


def get_uc_req_id(user_id: str):
    '''Returns a get profile by ID request'''
    return uc_get.GetProfileByIDRequest(
        requester='507f1f77bcf86cd799439011',
        user_id=user_id,
    )


def get_uc_req_name(username: str):
    '''Returns a get profile by username request'''
    return uc_get.GetProfileByUsernameRequest(
        requester='507f1f77bcf86cd799439011',
        username=username,
    )


# =======================================
# =                TESTS                =
# =======================================

def get_success_parameters():
    '''Returns parameters for "success" test'''
    user_self = get_user_self()
    uc_res_self = get_uc_res_self(user_self)
    user_friend = get_user_friend()
    uc_res_friend = get_uc_res_friend(user_friend)
    user_stranger = get_user_stranger()
    uc_res_stranger = get_uc_res_stranger(user_stranger)
    return [
        (user_self, uc_res_self),
        (user_friend, uc_res_friend),
        (user_stranger, uc_res_stranger),
    ]


@pytest.mark.parametrize("get_by", ['id', 'username'])
@pytest.mark.parametrize("user,uc_res", get_success_parameters())
@pytest.mark.asyncio
async def test_success(get_by, user, uc_res):
    '''Should return a user profile'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get.return_value = user
    user_repo.get_by_username.return_value = user

    # Create request
    if get_by == 'id':
        uc_req = get_uc_req_id(user.id)
    else:
        uc_req = get_uc_req_name(user.display_name)

    # Call usecase
    uc = uc_get.GetProfileUsercase(user_repo)
    res = await uc.execute(uc_req)

    # Assert results
    if get_by == 'id':
        user_repo.get.assert_called_with(user.id)
    else:
        user_repo.get_by_username.assert_called_with(user.username)
    assert res == uc_res


@pytest.mark.parametrize("get_by", ['id', 'username'])
@pytest.mark.parametrize("user,uc_res", get_success_parameters())
@pytest.mark.asyncio
async def test_fail(get_by, user, uc_res):
    '''Should return a UserNotFoundError'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get.return_value = None
    user_repo.get_by_username.return_value = None

    # Create request
    if get_by == 'id':
        uc_req = get_uc_req_id(user.id)
    else:
        uc_req = get_uc_req_name(user.display_name)

    # Call usecase
    uc = uc_get.GetProfileUsercase(user_repo)
    with pytest.raises(uc_get.UserNotFoundError):
        await uc.execute(uc_req)

    # Assert results
    if get_by == 'id':
        user_repo.get.assert_called_with(user.id)
    else:
        user_repo.get_by_username.assert_called_with(user.username)
