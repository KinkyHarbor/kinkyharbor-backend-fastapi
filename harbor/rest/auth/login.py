'''This module contains all login related routes'''

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, constr, Field
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from harbor.domain.common import Message
from harbor.domain.token import AccessToken, AccessRefreshTokens
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import login as uc_user_login


router = APIRouter()


class Credentials(BaseModel):
    '''Basic model for credentials'''
    login: constr(min_length=1) = Field(..., title='Username or email')
    password: constr(min_length=1)


@router.post('/login/', response_model=AccessRefreshTokens, responses={401: {"model": Message}})
async def login(creds: Credentials, repos: RepoDict = Depends(get_repos)):
    '''Trades username and password for an access token (custom implementation)'''
    try:
        uc = uc_user_login.LoginUseCase(repos['user'], repos['refresh_token'])
        uc_req = uc_user_login.LoginRequest(
            login=creds.login,
            password=creds.password
        )
        return await uc.execute(uc_req)

    except uc_user_login.InvalidCredsError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'Incorrect username or password'},
        )

    except uc_user_login.UserLockedError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'User is locked'},
        )


@router.post("/login/token/", summary='oauth2 password grant flow', response_model=AccessToken)
async def login_for_access_token(creds: OAuth2PasswordRequestForm = Depends(),
                                 repos: RepoDict = Depends(get_repos)):
    '''Trades username and password for an access token (oauth2: password grant)'''
    try:
        uc = uc_user_login.LoginUseCase(repos['user'], repos['refresh_token'])
        uc_req = uc_user_login.LoginRequest(
            login=creds.username,
            password=creds.password
        )
        tokens = await uc.execute(uc_req)
        return AccessToken(
            token=tokens.access_token,
            access_token=tokens.access_token,
            token_type="bearer"
        )

    except uc_user_login.InvalidCredsError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except uc_user_login.UserLockedError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is locked",
            headers={"WWW-Authenticate": "Bearer"},
        )
