'''Test cases for crud stats module'''
# pylint: disable=unused-argument

import uuid
from datetime import datetime, timedelta, timezone, date

import pytest

from harbor.domain import stats
from harbor.helpers.settings import get_settings
from harbor.repository.mongo.stats import create_repo


@pytest.fixture(name='reading')
async def fixture_reading(monkeypatch, event_loop):
    '''Returns a dummy reading'''
    return stats.Reading(
        datetime=datetime(2020, 5, 10, 15, 9, 54, 0, timezone.utc),
        subject=stats.ReadingSubject.ACTIVE_USERS,
        unit="users",
        value=50,
    )


@pytest.fixture(name='repo')
async def fixture_repo(monkeypatch, event_loop):
    '''Returns a temporary stats repo for testing'''
    appendix = str(uuid.uuid4()).replace('-', '')[:10]
    monkeypatch.setenv("MONGO_DATABASE", f"test-kh-stats-{appendix}")
    get_settings.cache_clear()
    repo = await create_repo()
    yield repo
    repo.client.drop_database(repo.db)


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_stats_roundtrip(repo, reading):
    '''Tests to upsert and fetch readings'''
    # Setup test
    subject = stats.ReadingSubject.ACTIVE_USERS

    # Simple round trip
    await repo.upsert(reading)
    result = await repo.get_latest(subject)
    assert reading == result

    # Insert newer reading
    newer_reading = reading.copy()
    newer_reading.datetime += timedelta(days=1)
    await repo.upsert(newer_reading)
    result = await repo.get_latest(subject)
    assert newer_reading == result
    assert newer_reading.datetime > reading.datetime

    # Update newer reading
    updated_reading = newer_reading.copy()
    updated_reading.value += 99
    await repo.upsert(updated_reading)
    result = await repo.get_latest(subject)
    assert updated_reading == result
    assert updated_reading.value > newer_reading.value


async def insert_readings(repo, base_reading):
    '''Inserts 5 dummy readings in the database'''
    for _ in range(5):
        base_reading.datetime += timedelta(days=1)
        base_reading.value += 10
        await repo.upsert(base_reading)


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_stats_by_month(repo, reading):
    '''Tests to aggregate readings by month'''
    # Insert readings
    await insert_readings(repo, reading.copy())
    future_reading = reading.copy()
    future_reading.datetime += timedelta(days=35)
    future_reading.value = 55
    await insert_readings(repo, future_reading)

    # Expected
    expected = stats.ReadingAggregation(
        subject=stats.ReadingSubject.ACTIVE_USERS,
        timespan=stats.ReadingAggregationTimespan.MONTH,
        operation=stats.ReadingAggregationOperation.AVERAGE,
        values={
            date(2020, 5, 1): 80,
            date(2020, 6, 1): 85,
        }
    )

    # Get aggregated result
    time_since_reading = datetime.now(timezone.utc) - reading.datetime
    result = await repo.get_by_month(
        subject=expected.subject,
        operation=expected.operation,
        from_=(-time_since_reading - timedelta(days=1)),
        to=(-time_since_reading + timedelta(days=60)),
    )

    # Assert result
    assert result == expected
