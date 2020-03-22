'''Unit tests for User Login usecase'''

from unittest import mock

import pytest

from harbor.domain.user import UserWithPassword
from harbor.repository.base import UserRepo, RefreshTokenRepo
from harbor.use_cases.user import login as uc_user_login


@pytest.fixture(name='test_user')
def fixture_test_user():
    '''Returns a test user'''
    return UserWithPassword(
        id='507f1f77bcf86cd799439011',
        display_name='TestUser',
        email='test@example.com',
        # Hashed value: TestPassword
        password_hash='$2y$12$ZKT/mZrO0966XsQrigPMXuQ0NupC/vWYrQIQFPHbH682EYdHiyFz2',
    )


@pytest.mark.asyncio
async def test_uc_user_login_success(test_user):
    '''Tests happy flow of User Login usecase'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = test_user
    rt_repo = mock.Mock(RefreshTokenRepo)

    # Call usecase
    uc_req = uc_user_login.LoginRequest(
        login='TestUser',
        password='TestPassword'
    )
    uc = uc_user_login.LoginUseCase(user_repo, rt_repo)
    tokens = await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('testuser')
    user_repo.update_last_login.assert_called_with('507f1f77bcf86cd799439011')
