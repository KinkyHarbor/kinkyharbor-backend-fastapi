'''User wants to update their profile'''

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.user import UserInfo
from harbor.helpers import debug
from harbor.repository.base import UserRepo


class UpdateProfileRequest(BaseModel):
    '''Request for update profile usecase'''
    user_id: ObjectIdStr
    bio: str = None
    gender: str = None


class UpdateProfileUseCase:
    '''User wants to update their profile'''

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self, req: UpdateProfileRequest) -> bool:
        '''Updates and returns the profile'''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Update the profile
        user_info = UserInfo(
            **req.dict(exclude={'user_id'}, exclude_unset=True)
        )
        return await self.user_repo.set_info(req.user_id, user_info)
