'''Helpers module for authentication related functions'''

from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from harbor.domain.token import AccessTokenData
from harbor.helpers.settings import get_settings, get_jwt_key

PASSLIB_OPTS = {
    'schemes': ['bcrypt'],
    'deprecated': 'auto',
}


def verify_password(plain_password, password_hash):
    '''Verify if password matches hashed password'''
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.verify(plain_password, password_hash)


def get_password_hash(password):
    '''Generates password hash from password'''
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.hash(password)


async def create_access_token(*, user_id: str, expires_delta: timedelta = None):
    '''Generates an access token containing provided data'''
    # Get settings
    settings = get_settings()

    # Prepare contents
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.utcnow() + timedelta(minutes=minutes)
    data = {
        "sub": f"user:{user_id}",
        "exp": expire,
    }

    # Generate token
    jwt_key_private = get_jwt_key('private')
    return jwt.encode(data, jwt_key_private, algorithm=settings.JWT_ALG)


class InvalidTokenError(Exception):
    '''Provided token is invalid'''


async def validate_access_token(token: str) -> AccessTokenData:
    '''Validates and extracts User ID from token

    Raises
        InvalidTokenError: Provided token is invalid
    '''
    # Get settings
    settings = get_settings()

    # Decode JWT token
    try:
        jwt_key_public = get_jwt_key('public')
        payload = jwt.decode(token, jwt_key_public,
                             algorithms=[settings.JWT_ALG])
    except jwt.PyJWTError:
        raise InvalidTokenError(f'Unable to decode token "{token}"')

    # Extract user ID
    try:
        user_id = payload.get("sub").split(':')[1]
    except IndexError:
        raise InvalidTokenError(
            f"Token payload doesn't contain valid user ID. Payload: {payload!r}"
        )

    # Build access token data
    try:
        return AccessTokenData(user_id=user_id)
    except ValidationError:
        raise InvalidTokenError(
            f'JWT token contains invalid user ID: "{user_id!r}"'
        )
