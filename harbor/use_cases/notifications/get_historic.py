'''User requests their historic notifications'''

from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr
from harbor.domain.notification import Notification
from harbor.helpers import debug
from harbor.repository.base import NotificationRepo


class GetHistoricRequest(BaseModel):
    '''Request for historic notifications'''
    user_id: ObjectIdStr
    from_: datetime
    to: datetime


class MaxTimeRangeExceeded(Exception):
    '''Maximum time range of 90 days exceeded'''


class GetHistoricUsecase:
    '''User requests their historic notifications'''

    def __init__(self, notif_repo: NotificationRepo):
        self.notif_repo = notif_repo

    async def execute(self, req: GetHistoricRequest) -> List[Notification]:
        '''Get historic notifications'''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Check if time range is valid
        if (req.to - req.from_) > timedelta(days=90):
            raise MaxTimeRangeExceeded('max 90 days')

        return await self.notif_repo.get_historic(req.user_id, req.from_, req.to)
