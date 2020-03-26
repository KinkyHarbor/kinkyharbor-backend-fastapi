'''This module contains all authentication related routes'''

from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, constr

from harbor.domain.common import ObjectIdStr, StrongPasswordStr, Message
from harbor.domain.email import EmailAddress
from harbor.domain.token import AccessToken, AccessRefreshTokens
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import (
    login as uc_user_login,
    register as uc_user_register,
    register_verify as uc_user_reg_verify,
    reset_password_exec as uc_user_reset_pw_exec,
    reset_password_req as uc_user_reset_pw_req,
    token_refresh as uc_token_refresh,
)


router = APIRouter()


@router.post('/register/', response_model=Message, responses={409: {"model": Message}})
async def register(req: uc_user_register.RegisterRequest,
                   background_tasks: BackgroundTasks,
                   repos: RepoDict = Depends(get_repos)):
    '''Register a new user'''
    uc = uc_user_register.RegisterUseCase(
        repos['user'],
        repos['verif_token'],
        background_tasks
    )

    try:
        await uc.execute(req)
        return {'msg': 'User created successfully'}

    except uc_user_register.UsernameReservedError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={'msg': 'This is a reserved username'},
        )

    except uc_user_register.UsernameTakenError:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content={'msg': 'Username already taken'},
        )


class RegisterVerifyBody(BaseModel):
    '''POST model to verify registration'''
    secret: constr(min_length=1)


@router.post('/register/verify/', response_model=Message)
async def verify_registration(token_secret: RegisterVerifyBody,
                              repos: RepoDict = Depends(get_repos)):
    '''User wants to verify his registration'''
    # Setup usecase and usecase request
    uc = uc_user_reg_verify.RegisterVerifyUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
    )
    uc_req = uc_user_reg_verify.RegisterVerifyRequest(
        secret=token_secret.secret
    )

    try:
        # Execute usecase
        uc.execute(uc_req)
        return {'msg': 'Account is verified'}

    except uc_user_reg_verify.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content={'msg': 'Provided token is not valid'},
        )


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


class ReplaceRefreshToken(BaseModel):
    '''Request to replace a refresh and access token'''
    refresh_token: str


@router.post('/refresh/', response_model=AccessRefreshTokens, responses={401: {"model": Message}})
async def refresh(req: ReplaceRefreshToken, repos: RepoDict = Depends(get_repos)):
    '''Trades a refresh token to a new access and refresh token (custom implementation)'''
    uc = uc_token_refresh.TokenRefreshUseCase(rt_repo=repos['refresh_token'])
    uc_req = uc_token_refresh.TokenRefreshRequest(
        refresh_token=req.refresh_token
    )

    try:
        tokens = await uc.execute(uc_req)
        return tokens

    except uc_token_refresh.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={'msg': 'Invalid refresh token'}
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


@router.post("/login/request-password-reset/", response_model=Message)
async def request_password_reset(address: EmailAddress,
                                 background_tasks: BackgroundTasks,
                                 repos: RepoDict = Depends(get_repos)):
    '''User requests a password reset'''
    uc = uc_user_reset_pw_req.RequestPasswordResetUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
        background_tasks=background_tasks,
    )
    uc_req = uc_user_reset_pw_req.RequestPasswordResetRequest(
        email=address
    )
    await uc.execute(uc_req)
    return {'msg': 'Verification mail sent, if email is linked to an existing user'}


class PasswordResetBody(BaseModel):
    '''POST model to reset password'''
    user_id: ObjectIdStr
    token: str
    password: StrongPasswordStr


@router.post("/login/password-reset/", response_model=Message)
async def password_reset(body: PasswordResetBody,
                         repos: RepoDict = Depends(get_repos)):
    '''Verifies password reset token and sets new password'''
    uc = uc_user_reset_pw_exec.ExecResetPasswordUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
    )
    uc_req = uc_user_reset_pw_exec.ExecResetPasswordRequest(
        **body
    )

    try:
        result = uc.execute(uc_req)
        if result == uc_user_reset_pw_exec.ExecResetPasswordResponse.UPDATED:
            return {'msg': 'Password is updated'}

        if result == uc_user_reset_pw_exec.ExecResetPasswordResponse.UPDATED_AND_VERIFIED:
            return {'msg': 'Password is updated and account is verified'}

    except uc_user_reset_pw_exec.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'Provided token is not valid'}
        )
