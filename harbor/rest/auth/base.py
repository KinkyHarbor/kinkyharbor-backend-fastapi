'''This module contains all authentication related routes'''

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from harbor.domain.token import AccessTokenData
from harbor.helpers import auth
from harbor.rest.auth import (
    login as router_login,
    password_reset as router_pw_reset,
    refresh as router_refresh,
    register as router_register,
)

# Combine all auth routers
router = APIRouter()
router.include_router(router_login.router)
router.include_router(router_pw_reset.router)
router.include_router(router_refresh.router)
router.include_router(router_register.router)


async def validate_access_token(token: str = Depends(
        OAuth2PasswordBearer(tokenUrl='/auth/login/token/')
)) -> AccessTokenData:
    '''Validates and extracts User ID from token

    Raises
        HTTPException: Provided token is invalid
    '''
    try:
        return await auth.validate_access_token(token)
    except auth.InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
