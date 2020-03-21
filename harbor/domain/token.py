'''This module contains all token related models'''

import secrets
from datetime import datetime
from enum import Enum, unique
from typing import Optional

from pydantic import BaseModel, validator

from harbor.domain.common import DBModelMixin, ObjectIdStr


class AccessToken(BaseModel):
    '''Token which grants access to the application'''
    access_token: str = None
    token: str = None
    token_type: str


class AccessTokenData(BaseModel):
    '''Contains data which will be embedded into AccessToken'''
    user_id: ObjectIdStr


class AccessRefreshTokens(BaseModel):
    '''Model containing both Access and Refresh tokens'''
    access_token: str
    refresh_token: str


class SecretToken(BaseModel):
    '''Base token containing a secret'''
    secret: str = None
    created_on: datetime = None

    @validator('secret', pre=True, always=True)
    @classmethod
    def generate_secret(cls, secret):
        '''Generate new secret if not filled'''
        return secret or secrets.token_urlsafe()

    @validator('created_on', pre=True, always=True)
    @classmethod
    def set_created_on(cls, created_on):
        '''Set Created On if not filled'''
        return created_on or datetime.utcnow()


@unique
class VerificationPurposeEnum(str, Enum):
    '''Enum containing the purpose of a verification token'''
    REGISTER = 'register'
    RESET_PASSWORD = 'password'
    CHANGE_EMAIL = 'email'


class VerificationTokenRequest(SecretToken):
    '''Request for verification of account activation, password reset, ...'''
    purpose: VerificationPurposeEnum
    user_id: Optional[ObjectIdStr]

    @validator('user_id', always=True)
    @classmethod
    def user_id_required(cls, user_id, values):
        '''Check if user_id is mandatory based on whitelist'''
        if not (user_id or values['purpose'] in (VerificationPurposeEnum.REGISTER,)):
            raise ValueError(
                f'User_id is mandatory for purpose "{values["purpose"]}"')
        return user_id


class VerificationToken(VerificationTokenRequest, DBModelMixin):
    '''Provides verification for account activation, password reset, ...'''


class RefreshToken(SecretToken):
    '''Refresh token which could be traded to new refresh token and access token'''
    user_id: ObjectIdStr
