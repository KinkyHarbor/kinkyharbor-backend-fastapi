'''Unit tests for Auth helpers'''
# pylint: disable=unused-argument

from datetime import datetime, timedelta
from unittest import mock

import jwt
import pytest

from harbor.domain.token import AccessTokenData
from harbor.helpers import auth
from harbor.helpers.settings import get_settings


def test_password_hash_roundtrip():
    '''Should be able to hash password and compare if equal'''
    hash_ = auth.get_password_hash("SecurePassword")
    assert auth.verify_password("SecurePassword", hash_)


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt.encode')
@mock.patch('harbor.helpers.auth.get_jwt_key')
async def test_create_access_token_with_defaults(get_jwt_key, jwt_encode, freezer):
    '''Should return an access token'''
    # Create mocks
    get_jwt_key.return_value = 'test-private-key'
    jwt_encode.return_value = 'test-access-token'

    # Get settings
    settings = get_settings()

    # Call function
    token = await auth.create_access_token(user_id='test-user-id')

    # Assert results
    assert token == 'test-access-token'
    get_jwt_key.assert_called_with('private')
    jwt_encode.assert_called_with(
        {
            'sub': 'user:test-user-id',
            'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        'test-private-key',
        algorithm=settings.JWT_ALG,
    )


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt.encode')
@mock.patch('harbor.helpers.auth.get_jwt_key')
async def test_create_access_token_with_expire(get_jwt_key, jwt_encode, freezer):
    '''Should return an access token'''
    # Create mocks
    get_jwt_key.return_value = 'test-private-key'
    jwt_encode.return_value = 'test-access-token'

    # Get settings
    settings = get_settings()

    # Call function
    delta = timedelta(minutes=123456)
    token = await auth.create_access_token(user_id='test-user-id', expires_delta=delta)

    # Assert results
    assert token == 'test-access-token'
    get_jwt_key.assert_called_with('private')
    jwt_encode.assert_called_with(
        {
            'sub': 'user:test-user-id',
            'exp': datetime.utcnow() + delta,
        },
        'test-private-key',
        algorithm=settings.JWT_ALG,
    )


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt.decode')
@mock.patch('harbor.helpers.auth.get_jwt_key')
async def test_success_validate_access_token(get_jwt_key, jwt_decode):
    '''Should return an access token'''
    # Create mocks
    get_jwt_key.return_value = 'test-public-key'
    jwt_decode.return_value = {'sub': 'user:507f1f77bcf86cd799439011'}

    # Get settings
    settings = get_settings()

    # Call function
    data = await auth.validate_access_token(token='test-jwt-token')

    # Assert results
    get_jwt_key.assert_called_with('public')
    jwt_decode.assert_called_with(
        'test-jwt-token',
        'test-public-key',
        algorithms=[settings.JWT_ALG],
    )
    assert data == AccessTokenData(
        user_id='507f1f77bcf86cd799439011',
    )


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt.decode')
@mock.patch('harbor.helpers.auth.get_jwt_key')
async def test_fail_invalid_token_jwt_error(get_jwt_key, jwt_decode):
    '''Should throw InvalidTokenError'''
    # Create mocks
    get_jwt_key.return_value = 'test-public-key'
    jwt_decode.side_effect = jwt.PyJWTError

    # Get settings
    settings = get_settings()

    # Call function
    with pytest.raises(auth.InvalidTokenError):
        await auth.validate_access_token(token='test-jwt-token')

    # Assert results
    get_jwt_key.assert_called_with('public')
    jwt_decode.assert_called_with(
        'test-jwt-token',
        'test-public-key',
        algorithms=[settings.JWT_ALG],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('payload', [
    {'sub': 'invalid'},
    {'sub': 'user:invalid'},
])
@mock.patch('harbor.helpers.auth.jwt.decode')
@mock.patch('harbor.helpers.auth.get_jwt_key')
async def test_fail_invalid_token_other(get_jwt_key, jwt_decode, payload):
    '''Should throw InvalidTokenError'''
    # Create mocks
    get_jwt_key.return_value = 'test-public-key'
    jwt_decode.return_value = payload

    # Get settings
    settings = get_settings()

    # Call function
    with pytest.raises(auth.InvalidTokenError):
        await auth.validate_access_token(token='test-jwt-token')

    # Assert results
    get_jwt_key.assert_called_with('public')
    jwt_decode.assert_called_with(
        'test-jwt-token',
        'test-public-key',
        algorithms=[settings.JWT_ALG],
    )
