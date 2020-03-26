'''Core module for authentication related functions'''

from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext

from harbor.core import settings
from harbor.domain.token import AccessTokenData

PASSLIB_OPTS = {
    'schemes': ['bcrypt'],
    'deprecated': 'auto',
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/token/')


CREDENTIALS_ERROR = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, password_hash):
    '''Verify if password matches hashed password'''
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.verify(plain_password, password_hash)


def get_password_hash(password):
    '''Generates password hash from password'''
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.hash(password)


async def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    jwt_key_private = await settings.get_jwt_key('private')
    encoded_jwt = jwt.encode(to_encode, jwt_key_private,
                             algorithm=settings.JWT_ALG)
    return encoded_jwt


async def validate_access_token(token: str = Depends(oauth2_scheme)) -> AccessTokenData:
    '''Validates and extracts User ID from token

    Raises
        CREDENTIALS_ERROR: Provided token is invalid
    '''
    try:
        jwt_key_public = await settings.get_jwt_key('public')
        payload = jwt.decode(token, jwt_key_public,
                             algorithms=[settings.JWT_ALG])
        user_id: str = payload.get("sub").split(':')[1]
        if user_id is None:
            raise CREDENTIALS_ERROR
        return AccessTokenData(user_id=user_id)
    except jwt.PyJWTError:
        raise CREDENTIALS_ERROR
