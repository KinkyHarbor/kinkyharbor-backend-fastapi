from pydantic import BaseModel, EmailStr

from db.models import DBModelMixin


class BaseUser(BaseModel):
    '''Base class with properties shared among all user models'''
    username: str
    email: EmailStr


class User(BaseUser, DBModelMixin):
    '''Generic user used throughout the application'''
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False


class RegisterUser(BaseUser):
    password: str


class UserDBIn(BaseUser):
    hashed_password: str
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False


class UserDBOut(UserDBIn, DBModelMixin):
    pass
