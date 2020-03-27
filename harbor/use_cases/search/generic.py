'''User wants to search'''

from typing import List

from pydantic import BaseModel, constr

from harbor.domain.common import ObjectIdStr
from harbor.domain.user import BaseUser
from harbor.repository.base import UserRepo


class GenericSearchRequest(BaseModel):
    '''Request for generic search usecase'''
    query: constr(min_length=1)
    user_id: ObjectIdStr


class GenericSearchResponse(BaseModel):
    '''Result of generic search'''
    users: List[BaseUser]
    groups: List
    pages: List
    events: List


class GenericSearchUseCase:
    '''User wants to search'''

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self, req: GenericSearchRequest) -> GenericSearchResponse:
        '''Searches across users, groups, pages and events'''
        return GenericSearchResponse(
            users=await self.user_repo.get_search(req.user_id, req.query),
            groups=[],
            pages=[],
            events=[],
        )
