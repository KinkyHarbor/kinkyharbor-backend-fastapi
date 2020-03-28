'''This module contains all user related models'''

from enum import Enum, unique
from datetime import datetime
from typing import List

from pydantic import EmailStr, validator

from harbor.domain.common import DBModelMixin, DisplayNameStr, ObjectIdStr


class BaseUser(DBModelMixin):
    '''Base users containing only minimal fields'''
    display_name: DisplayNameStr
    username: str = None

    @validator('username', pre=True, always=True)
    @classmethod
    def lowercase_display_name(cls, _, values):
        '''Converts display name to lowercase for username'''
        return values['display_name'].lower()


class User(BaseUser):
    '''General user to be used throughout the application'''
    # Core data
    email: EmailStr = None
    last_login: datetime = None
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False

    # Additional data
    bio: str = None
    gender: str = None
    friends: List[ObjectIdStr] = []


class UserWithPassword(User):
    '''User model including password hash'''
    password_hash: str


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
