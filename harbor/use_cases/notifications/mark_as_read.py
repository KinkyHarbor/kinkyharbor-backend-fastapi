'''User wants to mark one or more notifications as (un)read'''

from typing import List

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.notification import Notification
from harbor.repository.base import NotificationRepo


class MarkAsReadRequest(BaseModel):
    '''Request to mark one or more notifications as (un)read'''
    user_id: ObjectIdStr
    notifications: List[ObjectIdStr]
    is_read: bool


class MarkAsReadUsecase:
    '''User wants to mark one or more notifications as (un)read'''

    def __init__(self, notif_repo: NotificationRepo):
        self.notif_repo = notif_repo

    async def execute(self, req: MarkAsReadRequest) -> List[Notification]:
        '''Set is_read flag of notifications'''
        return await self.notif_repo.set_read(req.user_id, req.notifications, req.is_read)
