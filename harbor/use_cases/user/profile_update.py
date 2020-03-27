'''User wants to update their profile'''

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.repository.base import UserRepo


class UpdateProfileRequest(BaseModel):
    '''Request for update profile usecase'''
    user_id: ObjectIdStr
    bio: str = None
    gender: str = None


class UpdateProfileUsercase:
    '''User wants to update their profile'''

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self, req: UpdateProfileRequest) -> bool:
        '''Updates and returns the profile'''
        # Update the profile
        update_dict = req.dict(exclude={'user_id'}, exclude_unset=True)
        return await self.user_repo.set_info(req.user_id, update_dict)
