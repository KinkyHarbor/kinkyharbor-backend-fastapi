'''Unit tests for User Login usecase'''

from unittest import mock

import pytest

from harbor.domain.token import RefreshToken
from harbor.domain.user import UserWithPassword
from harbor.repository.base import UserRepo, RefreshTokenRepo
from harbor.use_cases.auth import login as uc_user_login


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a login request'''
    return uc_user_login.LoginRequest(
        login='TestUser',
        password='TestPassword'
    )


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
@mock.patch('harbor.core.auth.create_access_token')
async def test_uc_user_login_case_insensitive_success(create_access_token, uc_req, test_user):
    '''Should return an access and refresh token'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = test_user
    rt_repo = mock.Mock(RefreshTokenRepo)
    rt_repo.create_token.return_value = RefreshToken(
        user_id=test_user.id,
        secret='TestRefreshToken',
    )
    create_access_token.return_value = 'TestAccessToken'

    # Call usecase
    uc = uc_user_login.LoginUseCase(user_repo, rt_repo)
    tokens = await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('testuser')
    user_repo.update_last_login.assert_called_with(test_user.id)
    rt_repo.create_token.assert_called_with(test_user.id)
    assert tokens.access_token == 'TestAccessToken'
    assert tokens.refresh_token == f'{test_user.id}:TestRefreshToken'


@pytest.mark.asyncio
async def test_uc_user_not_found_fail(uc_req):
    '''Should throw InvalidCredsError if user is not found'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = None
    rt_repo = mock.Mock(RefreshTokenRepo)

    # Call usecase
    uc = uc_user_login.LoginUseCase(user_repo, rt_repo)
    tokens = None
    with pytest.raises(uc_user_login.InvalidCredsError):
        tokens = await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('testuser')
    user_repo.update_last_login.assert_not_called()
    assert tokens is None


@pytest.mark.asyncio
async def test_uc_invalid_password_fail(uc_req, test_user):
    '''Should throw InvalidCredsError if invalid password'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = test_user
    rt_repo = mock.Mock(RefreshTokenRepo)

    # Invalidate password
    uc_req.password = 'InvalidPassword'

    # Call usecase
    uc = uc_user_login.LoginUseCase(user_repo, rt_repo)
    tokens = None
    with pytest.raises(uc_user_login.InvalidCredsError):
        tokens = await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('testuser')
    user_repo.update_last_login.assert_not_called()
    assert tokens is None


@pytest.mark.asyncio
async def test_uc_user_locked_fail(uc_req, test_user):
    '''Should throw UserLockedError if user is locked'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    test_user.is_locked = True
    user_repo.get_by_login.return_value = test_user
    rt_repo = mock.Mock(RefreshTokenRepo)

    # Call usecase
    uc = uc_user_login.LoginUseCase(user_repo, rt_repo)
    tokens = None
    with pytest.raises(uc_user_login.UserLockedError):
        tokens = await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('testuser')
    user_repo.update_last_login.assert_not_called()
    assert tokens is None
