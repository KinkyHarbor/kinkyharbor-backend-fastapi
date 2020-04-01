'''Unit tests for User Profile Update usecase'''

from unittest import mock

import pytest

from harbor.repository.base import UserRepo
from harbor.use_cases.user import profile_update as uc_upd


@pytest.fixture(name='uc_req_all')
def fixture_uc_req_all():
    '''Returns a user profile update request'''
    return uc_upd.UpdateProfileRequest(
        user_id='507f1f77bcf86cd799439010',
        bio='test-bio',
        gender='test-gender',
    )


@pytest.fixture(name='uc_req_partial')
def fixture_uc_req_partial():
    '''Returns a partial user profile update request'''
    return uc_upd.UpdateProfileRequest(
        user_id='507f1f77bcf86cd799439010',
        bio='test-bio',
    )


@pytest.mark.parametrize("success", [True, False])
@pytest.mark.asyncio
async def test_all(success, uc_req_all):
    '''Should update profile info'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.set_info.return_value = success

    # Call usecase
    uc = uc_upd.UpdateProfileUsercase(user_repo)
    result = await uc.execute(uc_req_all)

    # Assert results
    user_repo.set_info.assert_called_with('507f1f77bcf86cd799439010', {
        'bio': 'test-bio',
        'gender': 'test-gender',
    })
    assert result is success


@pytest.mark.parametrize("success", [True, False])
@pytest.mark.asyncio
async def test_partial(success, uc_req_partial):
    '''Should update profile info'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.set_info.return_value = success

    # Call usecase
    uc = uc_upd.UpdateProfileUsercase(user_repo)
    result = await uc.execute(uc_req_partial)

    # Assert results
    user_repo.set_info.assert_called_with('507f1f77bcf86cd799439010', {
        'bio': 'test-bio',
    })
    assert result is success
