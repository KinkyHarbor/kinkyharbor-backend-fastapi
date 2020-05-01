'''This module contains all user related models'''

from enum import Enum, unique
from datetime import datetime
from typing import List

from pydantic import EmailStr, validator, BaseModel

from harbor.domain.common import DBModelMixin, DisplayNameStr, ObjectIdStr


class BaseUser(DBModelMixin):
    '''Base users containing only minimal fields'''
    display_name: DisplayNameStr
    username: str = None

    @validator('username', always=True)
    @classmethod
    def lowercase_display_name(cls, _, values):
        '''Username should match lowercase display name'''
        return values['display_name'].lower()


@unique
class UserRelation(str, Enum):
    '''Technical relation between users'''
    SELF = 'SELF'
    FRIEND = 'FRIEND'
    STRANGER = 'STRANGER'


class UserInfo(BaseModel):
    '''Optional user information'''
    bio: str = None
    gender: str = None


class User(BaseUser, UserInfo):
    '''General user to be used throughout the application'''
    # Core data
    email: EmailStr = None
    last_login: datetime = None
    is_admin: bool = False
    is_verified: bool = False
    is_locked: bool = False
    friends: List[ObjectIdStr] = []

    def get_relation(self, user_id: str) -> UserRelation:
        '''Get relation between this user and provided user

        Raises
            ValueError: self.id must be filled to check for relation SELF
        '''
        if self.id is None:
            raise ValueError("Can't get relation if self.id is empty")

        if self.id == user_id:
            return UserRelation.SELF

        if user_id in self.friends:
            return UserRelation.FRIEND

        return UserRelation.STRANGER


class UserWithPassword(User, UserInfo):
    '''User model including password hash'''
    password_hash: str


@unique
class UserFlags(str, Enum):
    '''Available flags on user profile'''
    ADMIN = 'is_admin'
    VERIFIED = 'is_verified'
    LOCKED = 'is_locked'


STRANGER_FIELDS = set([
    'id',
    'display_name',
    'username',
    'is_admin',
])

FRIEND_FIELDS = set([
    'bio',
    'gender',
    'friends',
    *STRANGER_FIELDS
])
