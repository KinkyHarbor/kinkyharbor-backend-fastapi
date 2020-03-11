'''This module contains all authentication related routes'''

from datetime import timedelta

from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB
from pydantic import BaseModel

from core import settings, auth, email
from core.db import get_db
from models.common import ObjectIdStr, StrongPasswordStr, Message
from models.email import EmailAddress
from models.token import (
    AccessToken,
    AccessRefreshTokens,
    RefreshToken,
    VerificationTokenRequest as VerifTokenReq,
    VerificationPurposeEnum as VerifPur,
)
from models.user import RegisterUser, UserFlags
from crud import users, verif_tokens, refresh_tokens


router = APIRouter()


@router.post('/register/', responses={409: {"model": Message}})
async def register(reg_user: RegisterUser,
                   background_tasks: BackgroundTasks,
                   db: MotorDB = Depends(get_db)):
    '''Register a new user'''
    # Check if username is reserved
    username = reg_user.username.lower()
    if username in settings.RESERVED_USERNAMES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="This is a reserved username. Please choose another one.",
        )

    # Create a new user in the database
    try:
        user = await users.register(db, reg_user)
    except DuplicateKeyError as error:
        if 'username' in str(error):
            return JSONResponse(
                status_code=HTTP_409_CONFLICT,
                content={'msg': 'Username already taken'},
            )
        user = None

    recipient = email.get_address(reg_user.username, reg_user.email)
    if user:
        # Get verification token
        token = await verif_tokens.create_verif_token(
            db, user.id, VerifPur.REGISTER)

        # Send verification mail
        msg = email.prepare_register_verification(recipient, token.secret)
    else:
        # Send password reset mail
        msg = email.prepare_register_email_exist(recipient)

    background_tasks.add_task(email.send_mail, msg)
    return {'msg': 'User created successfully'}


class RegisterVerifyBody(BaseModel):
    '''POST model to verify registration'''
    secret: str


@router.post('/register/verify/')
async def verify_registration(token_secret: RegisterVerifyBody, db: MotorDB = Depends(get_db)):
    token = VerifTokenReq(secret=token_secret.secret,
                          purpose=VerifPur.REGISTER)
    valid = await verif_tokens.verify_verif_token(db, token)
    if not valid:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Provided token is not valid"
        )

    # Mark account as verified
    await users.set_flag(db, valid.user_id, UserFlags.VERIFIED, True)
    return {'msg': 'Account is verified'}


class LoginUser(BaseModel):
    '''Basic model for credentials'''
    username: str
    password: str


@router.post('/login/', responses={
    200: {"model": AccessRefreshTokens},
    401: {"model": Message},
})
async def login(creds: LoginUser, db: MotorDB = Depends(get_db)):
    '''Trades username and password for an access token (custom implementation)'''
    try:
        user = await auth.authenticate_user(db, creds.username, creds.password)
    except auth.InvalidCredsError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'Incorrect username or password'},
        )
    except auth.UserLockedError:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'User is locked'},
        )

    # Authentication successful
    access_token = await auth.create_access_token(data={"sub": f'user:{user.id}'})
    refresh_token = await refresh_tokens.create_token(db, user.id)
    return AccessRefreshTokens(
        access_token=access_token,
        refresh_token=refresh_token.secret,
    )


class ReplaceRefreshToken(BaseModel):
    '''Request to replace a refresh and access token'''
    user_id: ObjectIdStr
    token: str


@router.post('/refresh/', responses={
    200: {"model": AccessRefreshTokens},
    401: {"model": Message},
})
async def refresh(req: ReplaceRefreshToken, db: MotorDB = Depends(get_db)):
    '''Trades a refresh token to a new access and refresh token'''
    old_ref_token = RefreshToken(secret=req.token, user_id=req.user_id)
    new_ref_token = await refresh_tokens.replace_token(db, old_ref_token)
    access_token = await auth.create_access_token(data={"sub": f'user:{req.user_id}'})

    if new_ref_token:
        return AccessRefreshTokens(
            access_token=access_token,
            refresh_token=new_ref_token.secret,
        )

    return JSONResponse(
        status_code=401,
        content={'msg': 'Invalid refresh token'}
    )


@router.post("/login/token/", summary='oauth2 password grant flow', response_model=AccessToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: MotorDB = Depends(get_db)):
    '''Trades username and password for an access token (oauth2: password grant)'''
    try:
        user = await auth.authenticate_user(db, form_data.username, form_data.password)
    except auth.InvalidCredsError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.UserLockedError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is locked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Authentication successful
    access_token = await auth.create_access_token(data={"sub": f'user:{user.id}'})
    return AccessToken(
        token=access_token,
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/login/request-password-reset/")
async def request_password_reset(address: EmailAddress,
                                 background_tasks: BackgroundTasks,
                                 db: MotorDB = Depends(get_db)):
    user = await users.get_login(db, address.email)
    if user:
        # User found => Send verification token
        token = await verif_tokens.create_verif_token(db, user.id, VerifPur.RESET_PASSWORD)
        recipient = email.get_address(user.username, user.email)
        msg = email.prepare_reset_password(
            recipient, token.user_id, token.secret)
        background_tasks.add_task(email.send_mail, msg)
    return {'msg': 'Verification mail sent, if email is linked to an existing user'}


class PasswordResetBody(BaseModel):
    '''POST model to reset password'''
    user_id: ObjectIdStr
    token: str
    password: StrongPasswordStr


@router.post("/login/password-reset/")
async def password_reset(body: PasswordResetBody,
                         db: MotorDB = Depends(get_db)):
    token = VerifTokenReq(secret=body.token,
                          user_id=body.user_id,
                          purpose=VerifPur.RESET_PASSWORD)
    valid = await verif_tokens.verify_verif_token(db, token)
    if not valid:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Provided token is not valid"
        )

    # Set new password
    user = await users.set_password(db, valid.user_id, body.password)

    # Mark account as verified
    if not user.is_verified:
        await users.set_flag(db, valid.user_id, UserFlags.VERIFIED, True)
        return {'msg': 'Password is updated and account is verified'}
    return {'msg': 'Password is updated'}
