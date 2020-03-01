'''This module contains all user related models'''

from enum import Enum, unique

from pydantic import BaseModel, EmailStr, validator

from models.common import DBModelMixin, DisplayNameStr


class BaseUser(BaseModel):
    '''Base class with properties shared among all user models'''
    display_name: DisplayNameStr
    username: str = None
    email: EmailStr

    @validator('username', pre=True, always=True)
    @classmethod
    def lowercase_display_name(cls, _, values):
        '''Converts display name to lowercase for username'''
        return values['display_name'].lower()


class User(BaseUser, DBModelMixin):
    '''Generic user used throughout the application'''
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False


class RegisterUser(BaseModel):
    '''Required form data for registering a user'''
    username: DisplayNameStr
    email: EmailStr
    password: str


class UserDBIn(BaseUser):
    hashed_password: str
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False


class UserDBOut(UserDBIn, DBModelMixin):
    pass


@unique
class UserFlags(Enum):
    ADMIN = 'is_admin'
    VERIFIED = 'is_verified'
    LOCKED = 'is_locked'
