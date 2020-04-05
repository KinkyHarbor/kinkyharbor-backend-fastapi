'''Unit tests for Refresh Token usecase'''
# pylint: disable=unused-argument

from unittest import mock

import pytest

from harbor.domain.token import RefreshToken
from harbor.repository.base import RefreshTokenRepo
from harbor.use_cases.auth import token_refresh as uc_ref


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a refresh tokens request'''
    return uc_ref.TokenRefreshRequest(
        refresh_token='507f1f77bcf86cd799439111:-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
    )


@pytest.fixture(name='refresh_token')
def fixture_refresh_token(freezer):
    '''Returns a refresh token'''
    return RefreshToken(
        user_id='507f1f77bcf86cd799439111',
        secret='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
    )


@pytest.mark.asyncio
@mock.patch('harbor.core.auth.create_access_token')
async def test_success(create_access_token, uc_req, refresh_token, freezer):
    '''Should return an access and refresh token'''
    # Create mocks
    rt_repo = mock.Mock(RefreshTokenRepo)
    rt_repo.replace_token.return_value = RefreshToken(
        user_id='507f1f77bcf86cd799439111',
        secret='TestRefreshToken',
    )
    create_access_token.return_value = 'TestAccessToken'

    # Call usecase
    uc = uc_ref.TokenRefreshUseCase(rt_repo)
    tokens = await uc.execute(uc_req)

    # Assert results
    rt_repo.replace_token.assert_called_with(refresh_token)
    assert tokens.access_token == 'TestAccessToken'
    assert tokens.refresh_token == '507f1f77bcf86cd799439111:TestRefreshToken'


@pytest.mark.asyncio
async def test_fail_invalid_token(freezer, uc_req, refresh_token):
    '''Should throw InvalidTokenError'''
    # Create mocks
    rt_repo = mock.Mock(RefreshTokenRepo)
    rt_repo.replace_token.return_value = None

    # Call usecase
    uc = uc_ref.TokenRefreshUseCase(rt_repo)
    with pytest.raises(uc_ref.InvalidTokenError):
        await uc.execute(uc_req)

    # Assert results
    rt_repo.replace_token.assert_called_with(refresh_token)
