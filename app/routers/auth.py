from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import logging

from models.user import UserInDB, RegisterUser
from crud import users


router = APIRouter()


@router.post('/register')
async def register(user: RegisterUser):
    await users.add(user.dict())


@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = await users.get_login(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)

    if not user.hashed_password == hashed_password:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Incorrect username or password")

    return {"access_token": user.id, "token_type": "bearer"}
