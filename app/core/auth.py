from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


def decode_token(token: str):
    return User(id=token)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
