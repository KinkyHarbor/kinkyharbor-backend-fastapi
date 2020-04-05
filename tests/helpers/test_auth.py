'''Unit tests for Auth helpers'''
# pylint: disable=unused-argument

from datetime import datetime, timedelta
from unittest import mock

import pytest

from harbor.helpers import auth, settings


def test_password_hash_roundtrip():
    '''Should be able to hash password and compare if equal'''
    hash_ = auth.get_password_hash("SecurePassword")
    assert auth.verify_password("SecurePassword", hash_)


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt')
@mock.patch('harbor.helpers.auth.settings.get_jwt_key')
async def test_create_access_token_with_defaults(get_jwt_key, jwt, freezer):
    '''Should return an access token'''
    # Create mocks
    get_jwt_key.return_value = 'test-private-key'
    jwt.encode.return_value = 'test-access-token'

    # Call function
    token = await auth.create_access_token(user_id='test-user-id')

    # Assert results
    assert token == 'test-access-token'
    get_jwt_key.assert_called_with('private')
    jwt.encode.assert_called_with(
        {
            'sub': 'user:test-user-id',
            'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        'test-private-key',
        algorithm=settings.JWT_ALG,
    )


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.jwt')
@mock.patch('harbor.helpers.auth.settings.get_jwt_key')
async def test_create_access_token_with_expire(get_jwt_key, jwt, freezer):
    '''Should return an access token'''
    # Create mocks
    get_jwt_key.return_value = 'test-private-key'
    jwt.encode.return_value = 'test-access-token'

    # Call function
    delta = timedelta(minutes=123456)
    token = await auth.create_access_token(user_id='test-user-id', expires_delta=delta)

    # Assert results
    assert token == 'test-access-token'
    get_jwt_key.assert_called_with('private')
    jwt.encode.assert_called_with(
        {
            'sub': 'user:test-user-id',
            'exp': datetime.utcnow() + delta,
        },
        'test-private-key',
        algorithm=settings.JWT_ALG,
    )
