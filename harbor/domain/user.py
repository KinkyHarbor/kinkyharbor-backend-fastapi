'''This module contains all user related models'''

from enum import Enum, unique
from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, validator, Field

from harbor.domain.common import DBModelMixin, DisplayNameStr, StrongPasswordStr, ObjectIdStr


class RegisterUser(BaseModel):
    '''Required form data for registering a user'''
    username: DisplayNameStr
    email: EmailStr
    password: StrongPasswordStr = Field(...,
                                        description='Password should either be 16 characters or '
                                        'longer (passphrase). Or should be minimum 8 long and '
                                        'have lower case, upper case and a digit.')
    isAdult: bool = Field(...,
                          title='Is adult',
                          description='Confirms the user is an adult')
    acceptPrivacyAndTerms: bool

    @validator('isAdult')
    @classmethod
    def must_be_adult(cls, is_adult):
        '''User must be an adult'''
        if not is_adult:
            raise ValueError('User must be an adult')
        return True

    @validator('acceptPrivacyAndTerms')
    @classmethod
    def must_accept_priv_and_terms(cls, accepted):
        '''User must accept Privacy policy and Terms and conditions'''
        if not accepted:
            raise ValueError(
                'User must accept Privacy policy and Terms and conditions to use this platform')
        return True


class BaseUser(BaseModel):
    '''Base class with properties shared among all user models'''
    # Core data
    display_name: DisplayNameStr
    username: str = None
    email: EmailStr
    last_login: datetime = None
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False

    # Additional data
    bio: str = None
    gender: str = None
    friends: List[ObjectIdStr] = []

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
    '''Available flags on user profile'''
    ADMIN = 'is_admin'
    VERIFIED = 'is_verified'
    LOCKED = 'is_locked'


STRANGER_FIELDS = {
    'id',
    'display_name',
    'username',
    'is_admin',
}

FRIEND_FIELDS = {
    'bio',
    'gender',
    'friends',
    *STRANGER_FIELDS
}


class UpdateUser(BaseModel):
    '''Info which allows direct update'''
    bio: str = None
    gender: str = None


class SearchUser(DBModelMixin):
    '''User returned in search results'''
    display_name: DisplayNameStr
    username: str
