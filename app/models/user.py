import re

from pydantic import BaseModel, EmailStr, validator

from db.models import DBModelMixin


class BaseUser(BaseModel):
    '''Base class with properties shared among all user models'''
    username: str
    email: EmailStr

    @validator('username')
    def username_only_valid_chars(cls, username):
        match = re.search(r'[^a-zA-Z0-9_\-]', username)
        if match:
            raise ValueError(
                "Username should only contain alphanumerical "
                "characters, '-' or '_'. Invalid character: " +
                match.group())
        return username


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
