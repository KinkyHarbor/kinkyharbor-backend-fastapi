'''This module contains all token related models'''

import secrets
from datetime import datetime
from enum import Enum, unique
from typing import Optional

from pydantic import BaseModel, validator

from models.common import DBModelMixin, ObjectIdStr


class AccessToken(BaseModel):
    '''Token which grants access to the application'''
    access_token: str
    token_type: str


class AccessTokenData():
    '''Contains data which will be embedded into AccessToken'''
    user_id: ObjectIdStr


@unique
class VerificationPurposeEnum(str, Enum):
    '''Enum containing the purpose of a verification token'''
    REGISTER = 'register'
    RESET_PASSWORD = 'password'
    CHANGE_EMAIL = 'email'


class TokenSecret(BaseModel):
    secret: str


class VerificationTokenRequest(BaseModel):
    '''Request for verification of account activation, password reset, ...'''
    secret: str = secrets.token_urlsafe()
    created_on: datetime = datetime.utcnow()
    purpose: VerificationPurposeEnum
    user_id: Optional[ObjectIdStr]

    @validator('user_id')
    def user_id_required(cls, user_id, values):
        # Check if user_id is mandatory based on whitelist
        if not (user_id or values['purpose'] in (VerificationPurposeEnum.REGISTER,)):
            raise ValueError(
                f'User_id is mandatory for purpose "{values["purpose"]}"')
        return user_id


class VerificationToken(VerificationTokenRequest, DBModelMixin):
    '''Provides verification for account activation, password reset, ...'''
