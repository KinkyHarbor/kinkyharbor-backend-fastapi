'''This module contains all authentication related routes'''

import logging
from datetime import timedelta

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from core import settings, auth, email
from models.token import AccessToken, TokenSecret, VerificationTokenRequest as VerifTokenReq, VerificationPurposeEnum as VerifPur
from models.user import RegisterUser, UserFlags
from crud import users, verif_tokens
from db.mongo import get_db


router = APIRouter()


@router.post('/register')
async def register(reg_user: RegisterUser,
                   background_tasks: BackgroundTasks,
                   db: MotorDB = Depends(get_db)):
    if reg_user.username in settings.RESERVED_USERNAMES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="This is a reserved username. Please choose another one.",
        )

    try:
        user = await users.register(db, reg_user, is_verified=settings.DEMO)
    except DuplicateKeyError as error:
        if 'username' in str(error):
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        if settings.DEMO and 'email' in str(error):
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Demo: There is already an account registered with this email",
            )

        user = None

    if not settings.DEMO:
        if user:
            # Get verification token
            token = await verif_tokens.create_verif_token(
                db, user.id, VerifPur.REGISTER)

            # Send verification mail
            subject = 'Verify your Kinky Harbor account'
            registration_link = f'http://kinkyharbor.com/register?token={token.secret}'
            msg = email.TEMPLATE_REGISTER_TEXT.format(
                registration_link=registration_link)
            msg_html = email.TEMPLATE_REGISTER_HTML.format(
                registration_link=registration_link)
        else:
            # Send password reset mail
            subject = 'Registration attempt at Kinky Harbor'
            reset_password_link = f'http://kinkyharbor.com/reset-password/'
            msg = email.TEMPLATE_REGISTER_EMAIL_EXISTS_TEXT.format(
                reset_password_link=reset_password_link)
            msg_html = email.TEMPLATE_REGISTER_EMAIL_EXISTS_HTML.format(
                reset_password_link=reset_password_link)

        to = email.get_address(reg_user.username, reg_user.email)
        background_tasks.add_task(email.send_mail, to, subject, msg, msg_html)
    return {'msg': 'User created successfully'}


@router.post('/register/verify')
async def verify_registration(token_secret: TokenSecret, db: MotorDB = Depends(get_db)):
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


@router.post("/token", response_model=AccessToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: MotorDB = Depends(get_db)):
    '''Trades username and password for an access token'''
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth.create_access_token(
        data={"sub": f'user:{user.id}'}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
