'''This module contains all user related models'''

from enum import Enum, unique
from datetime import datetime

from pydantic import BaseModel, EmailStr, validator

from models.common import DBModelMixin, DisplayNameStr


class RegisterUser(BaseModel):
    '''Required form data for registering a user'''
    username: DisplayNameStr
    email: EmailStr
    password: str


class BaseUser(BaseModel):
    '''Base class with properties shared among all user models'''
    display_name: DisplayNameStr
    username: str = None
    email: EmailStr
    last_login: datetime = None
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False

    @validator('username', pre=True, always=True)
    @classmethod
    def lowercase_display_name(cls, _, values):
        '''Converts display name to lowercase for username'''
        return values['display_name'].lower()


class User(BaseUser, DBModelMixin):
    '''Generic user used throughout the application'''


class UserDBIn(BaseUser):
    '''User model for insertion into database'''
    hashed_password: str


class UserDB(UserDBIn, DBModelMixin):
    '''User as stored in the database'''


@unique
class UserFlags(Enum):
    ADMIN = 'is_admin'
    VERIFIED = 'is_verified'
    LOCKED = 'is_locked'
