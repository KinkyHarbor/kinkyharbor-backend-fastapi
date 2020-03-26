'''User requests a user profile'''

import logging
from typing import Union

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.user import User, FRIEND_FIELDS, STRANGER_FIELDS
from harbor.repository.base import UserRepo


class GetProfileRequestBase(BaseModel):
    '''Base class for usecase request'''
    requester: ObjectIdStr


class GetProfileByIDRequest(GetProfileRequestBase):
    '''Request a user profile by ID'''
    user_id: ObjectIdStr


class GetProfileByUsernameRequest(GetProfileRequestBase):
    '''Request a user profile by username'''
    username: str


GetProfileRequest = Union[GetProfileByIDRequest, GetProfileByUsernameRequest]


class UserNotFoundError(Exception):
    '''No user is found'''


class GetProfileResponse(BaseModel):
    '''Result of get profile'''
    user: User
    is_self: bool
    is_friend: bool


class GetProfileUsercase:
    '''User requests a user profile'''

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self, req: GetProfileRequest) -> GetProfileResponse:
        '''Gets user profile by ID or username'''
        # Fetch user from repo
        if isinstance(req, GetProfileByIDRequest):
            user = await self.user_repo.get(req.user_id)
        elif isinstance(req, GetProfileByUsernameRequest):
            user = await self.user_repo.get_by_username(req.username.lower())

        # User not found
        if not user:
            raise UserNotFoundError

        logging.error(user)

        # User requested own profile
        if req.requester == user.id:
            return GetProfileResponse(
                user=user,
                is_self=True,
                is_friend=False,
            )

        # Restrict returned fields
        is_friend = req.requester in user.friends
        include_fields = FRIEND_FIELDS if is_friend else STRANGER_FIELDS
        filtered_user = User(
            **user.dict(include=include_fields),
            email='redacted@kinkyharbor.com'
        )
        return GetProfileResponse(
            user=filtered_user,
            is_self=False,
            is_friend=is_friend,
        )
