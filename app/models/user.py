import uuid
from typing import Optional
from pydantic import BaseModel, UUID4, EmailStr


class BaseUser(BaseModel):
    id: UUID4
    username: str
    email: EmailStr


class User(BaseUser):
    is_active: bool = False
    is_admin: bool = False


class UserInDB(User):
    hashed_password: str


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str
