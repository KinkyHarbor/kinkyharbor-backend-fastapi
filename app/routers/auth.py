from datetime import timedelta

from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from core import settings, auth
from models.token import Token
from models.user import RegisterUser
from crud import users
from db.mongo import get_db


router = APIRouter()


@router.post('/register')
async def register(user: RegisterUser, db: MotorDB = Depends(get_db)):
    await users.register(db, user, is_verified=settings.DEMO)
    return 'User created successfully'


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
