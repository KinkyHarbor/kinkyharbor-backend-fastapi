'''User requests a user profile'''

from typing import Union, List

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.user import User, UserRelation, FRIEND_FIELDS, STRANGER_FIELDS
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
    relation: UserRelation
    exposed_fields: List[str]


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

        # Get relation
        relation = user.get_relation(req.requester)

        # User requested own profile
        if relation == UserRelation.SELF:
            return GetProfileResponse(
                user=user,
                relation=UserRelation.SELF,
                exposed_fields=list(user.__fields__.keys()),
            )

        # Restrict returned fields
        include_fields = FRIEND_FIELDS if relation == UserRelation.FRIEND else STRANGER_FIELDS
        filtered_user = user.copy(include=include_fields)
        return GetProfileResponse(
            user=filtered_user,
            relation=relation,
            exposed_fields=include_fields,
        )
