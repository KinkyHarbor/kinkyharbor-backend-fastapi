from datetime import datetime, timedelta
import logging

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext

from core import settings
from models.user import User, UserDBOut
from models.token import TokenData
from crud import users
from db.mongo import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(db, username: str, password: str):
    user = await users.get_login(db, username)
    if not user:
        # Prevent timing attack
        get_password_hash(password)
        return False
    if not verify_password(password, user.hashed_password):
        return False
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


async def get_current_user(db=Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt_key_public = await settings.get_jwt_key('public')
        payload = jwt.decode(token, jwt_key_public,
                             algorithms=[settings.JWT_ALG])
        id: str = payload.get("sub").split(':')[1]
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except jwt.PyJWTError:
        raise credentials_exception
    user = await users.get(db, token_data.id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserDBOut = Depends(get_current_user)):
    if not current_user.is_locked:
        return current_user
    raise HTTPException(HTTP_400_BAD_REQUEST, detail="User is locked")
