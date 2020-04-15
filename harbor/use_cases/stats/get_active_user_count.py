'''User wants the active users count'''

import asyncio

from pydantic import BaseModel

from harbor.domain.stats import ReadingSubject, ReadingAggregation
from harbor.repository.base import StatsRepo


class GetActiveUserCountResponse(BaseModel):
    '''Result of get active user count'''
    now: int
    history: ReadingAggregation


class GetActiveUserCountUsecase:
    '''User requests the active user count'''

    def __init__(self, stats_repo: StatsRepo):
        self.stats_repo = stats_repo

    async def execute(self) -> GetActiveUserCountResponse:
        '''Get count of users which logged in during past month'''
        # Fetch counts
        co_now = self.stats_repo.get_latest(ReadingSubject.ACTIVE_USERS)
        co_history = self.stats_repo.get_by_month(ReadingSubject.ACTIVE_USERS)
        (now, history) = await asyncio.gather(co_now, co_history)

        # Return results
        return GetActiveUserCountResponse(now=now.value, history=history)
