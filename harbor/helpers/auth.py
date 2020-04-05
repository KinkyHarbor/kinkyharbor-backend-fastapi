'''Helpers module for authentication related functions'''

from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED
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


async def validate_access_token(token: str = Depends(
        OAuth2PasswordBearer(tokenUrl='/auth/login/token/')
)) -> AccessTokenData:
    '''Validates and extracts User ID from token

    Raises
        HTTPException: Provided token is invalid
    '''
    invalid_token_error = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt_key_public = await settings.get_jwt_key('public')
        payload = jwt.decode(token, jwt_key_public,
                             algorithms=[settings.JWT_ALG])
        user_id: str = payload.get("sub").split(':')[1]
        if user_id is None:
            raise invalid_token_error
        return AccessTokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise invalid_token_error
