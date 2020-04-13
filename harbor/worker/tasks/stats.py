'''This module contains stats tasks for Celery'''

import asyncio
from datetime import date, datetime

from harbor.domain.stats import Reading
from harbor.repository.mongo import stats
from harbor.worker.app import app


async def async_count_active_users():
    '''Count and store active users'''
    # Create dummy reading
    today = date.today()
    dummy_reading = Reading(
        datetime=datetime(today.year, today.month, today.day),
        subject="test",
        value=datetime.now().second,
        unit="stars",
    )

    # Save dummy reading
    stats_repo = await stats.create_repo()
    await stats_repo.set(dummy_reading)


@app.task
def count_active_users():
    '''Count and store active users'''
    # Make synchronous
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_count_active_users())
