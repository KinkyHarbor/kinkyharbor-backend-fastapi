from datetime import timedelta
from email.headerregistry import Address

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from core import settings, auth, email
from models.token import Token
from models.user import RegisterUser
from crud import users
from db.mongo import get_db


router = APIRouter()


@router.post('/register')
async def register(user: RegisterUser,
                   background_tasks: BackgroundTasks,
                   db: MotorDB = Depends(get_db)):
    if user.username in settings.RESERVED_USERNAMES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="This is a reserved username. Please choose another one.",
        )

    try:
        await users.register(db, user, is_verified=settings.DEMO)
        success = True
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

        success = False

    if not settings.DEMO:
        if success:
            # Send verification mail
            subject = 'Verify your Kinky Harbor account'
            registration_link = 'http://kinkyharbor.com/register'
            msg = email.TEMPLATE_REGISTER_TEXT.format(
                registration_link=registration_link)
            msg_html = email.TEMPLATE_REGISTER_HTML.format(
                registration_link=registration_link)
        else:
            # Send password reset mail
            subject = 'Registration attempt at Kinky Harbor'
            reset_password_link = 'http://kinkyharbor.com/reset-password'
            msg = email.TEMPLATE_REGISTER_EMAIL_EXISTS_TEXT.format(
                reset_password_link=reset_password_link)
            msg_html = email.TEMPLATE_REGISTER_EMAIL_EXISTS_HTML.format(
                reset_password_link=reset_password_link)

        to = email.get_address(user.username, user.email)
        background_tasks.add_task(email.send_mail, to, subject, msg, msg_html)
    return {'msg': 'User created successfully'}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: MotorDB = Depends(get_db)):
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
