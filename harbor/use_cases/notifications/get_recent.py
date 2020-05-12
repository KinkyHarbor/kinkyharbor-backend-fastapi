'''User requests their recent notifications'''

from typing import List

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.notification import Notification
from harbor.helpers import debug
from harbor.repository.base import NotificationRepo


class GetRecentRequest(BaseModel):
    '''Request for recent notifications'''
    user_id: ObjectIdStr


class GetRecentUsecase:
    '''User requests their recent notifications'''

    def __init__(self, notif_repo: NotificationRepo):
        self.notif_repo = notif_repo

    async def execute(self, req: GetRecentRequest) -> List[Notification]:
        '''Get recent notifications'''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Get recent notifications
        return await self.notif_repo.get_recent(req.user_id)
