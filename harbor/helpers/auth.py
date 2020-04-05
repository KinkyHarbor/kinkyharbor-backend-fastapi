'''Helpers module for authentication related functions'''

from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from harbor.domain.token import AccessTokenData
from harbor.helpers import settings

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
    # Prepare contents
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "sub": f"user:{user_id}",
        "exp": expire,
    }

    # Generate token
    jwt_key_private = await settings.get_jwt_key('private')
    return jwt.encode(data, jwt_key_private, algorithm=settings.JWT_ALG)


class InvalidTokenError(Exception):
    '''Provided token is invalid'''


async def validate_access_token(token: str) -> AccessTokenData:
    '''Validates and extracts User ID from token

    Raises
        InvalidTokenError: Provided token is invalid
    '''
    try:
        jwt_key_public = await settings.get_jwt_key('public')
        payload = jwt.decode(token, jwt_key_public,
                             algorithms=[settings.JWT_ALG])
        user_id: str = payload.get("sub").split(':')[1]
        if user_id is None:
            raise InvalidTokenError(token)
        return AccessTokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise InvalidTokenError(token)
