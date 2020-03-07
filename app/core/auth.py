'''Core module for authentication related functions'''

from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext

from core import settings
from core.db import get_db
from models.user import User, UserDB
from models.token import AccessTokenData
from crud import users

PASSLIB_OPTS = {
    'schemes': ['bcrypt'],
    'deprecated': 'auto',
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/token')


class InvalidCredsError(Exception):
    '''Provided credentials are invalid'''


class UserLockedError(Exception):
    '''User is locked'''


CREDENTIALS_ERROR = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, hashed_password):
    '''Verify if password matches hashed password'''
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.verify(plain_password, hashed_password)


def get_password_hash(password):
    ctx = CryptContext(**PASSLIB_OPTS)
    return ctx.hash(password)


async def authenticate_user(db, username: str, password: str):
    '''Tries to authenticate a user

    Raises:
        InvalidCredsError: Provided credentials are invalid
        UserLockedError: User is locked
    '''
    user = await users.get_login(db, username)

    # Check if matching user was found
    if not user:
        # Prevent timing attack
        get_password_hash(password)
        raise InvalidCredsError()

    # Check if password is correct
    if not verify_password(password, user.hashed_password):
        raise InvalidCredsError()

    # Check if user is not locked
    if user.is_locked:
        raise UserLockedError()

    # Authentication successful
    await users.update_last_login(db, user.id)
    return user


async def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
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


async def get_current_user(db=Depends(get_db),
                           token_data: str = Depends(validate_access_token)) -> User:
    '''Get current user from User ID in token

    Raises
        CREDENTIALS_ERROR: User not found
    '''
    user = await users.get(db, token_data.user_id)
    if user is None:
        raise CREDENTIALS_ERROR
    return user


async def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    '''Get user if not locked

    Raises
        HTTPException: User is locked
    '''
    if current_user.is_locked:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="User is locked")
    return current_user
