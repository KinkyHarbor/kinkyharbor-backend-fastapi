'''User wants to mark one or more notifications as (un)read'''

from typing import List

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.helpers import debug
from harbor.repository.base import NotificationRepo


class MarkAsReadRequest(BaseModel):
    '''Request to mark one or more notifications as (un)read'''
    user_id: ObjectIdStr
    notification_ids: List[ObjectIdStr]
    is_read: bool


class MarkAsReadResponse(BaseModel):
    '''Response to mark one or more notifications as (un)read'''
    count_updated: int


class MarkAsReadUsecase:
    '''User wants to mark one or more notifications as (un)read'''

    def __init__(self, notif_repo: NotificationRepo):
        self.notif_repo = notif_repo

    async def execute(self, req: MarkAsReadRequest) -> MarkAsReadResponse:
        '''Set is_read flag of notifications'''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Mark notifications and return updated count
        count = await self.notif_repo.set_read(req.user_id, req.notification_ids, req.is_read)
        return MarkAsReadResponse(count_updated=count)
