'''This module contains stats tasks for Celery'''

import asyncio
from datetime import datetime, timezone

from harbor.domain.stats import Reading, ReadingSubject
from harbor.repository.mongo import stats, users
from harbor.worker.app import app


async def async_count_active_users():
    '''Count and store active users'''
    # Fetch active users
    count = 0
    async with users.UserMongoRepo() as user_repo:
        count = await user_repo.count_active_users()

    # Create reading
    today = datetime.now(timezone.utc)
    reading = Reading(
        datetime=datetime(today.year, today.month, today.day),
        subject=ReadingSubject.ACTIVE_USERS,
        value=count,
        unit="users",
    )

    # Save reading
    async with stats.StatsMongoRepo() as stats_repo:
        await stats_repo.upsert(reading)


@app.task
def count_active_users():
    '''Count and store active users'''
    # Make synchronous
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_count_active_users())
