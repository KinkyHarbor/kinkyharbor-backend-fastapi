'''User requests their historic notifications'''

from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel, validator

from harbor.domain.common import ObjectIdStr
from harbor.domain.notification import Notification
from harbor.repository.base import NotificationRepo


class GetHistoricRequest(BaseModel):
    '''Request for historic notifications'''
    user_id: ObjectIdStr
    from_: datetime
    to: datetime

    @validator('to')
    @classmethod
    def max_time_range(cls, value, values):
        '''Time range should be maximum 90 days'''
        if value - values['from_'] > timedelta(days=90):
            raise ValueError('Maximum time range of 90 days exceeded')
        return value


class GetHistoricUsecase:
    '''User requests their historic notifications'''

    def __init__(self, notif_repo: NotificationRepo):
        self.notif_repo = notif_repo

    async def execute(self, req: GetHistoricRequest) -> List[Notification]:
        '''Get historic notifications'''
        return await self.notif_repo.get_historic(req.user_id, req.from_, req.to)
