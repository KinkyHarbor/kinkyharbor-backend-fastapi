'''Unit tests for Stats worker tasks'''
# pylint: disable=unused-argument

from datetime import datetime, timezone
from unittest import mock

import pytest

from harbor.domain.stats import Reading, ReadingSubject
from harbor.worker.tasks.stats import async_count_active_users


@pytest.mark.asyncio
@mock.patch('harbor.worker.tasks.stats.StatsMongoRepo.__aenter__')
@mock.patch('harbor.worker.tasks.stats.UserMongoRepo.__aenter__')
async def test_count_active_users(mock_users_ctx, mock_stats_ctx, freezer):
    '''Should insert the current active user count in the database'''
    # Create mocks
    mock_users = mock.AsyncMock()
    mock_users.count_active_users.return_value = 99
    mock_users_ctx.return_value = mock_users

    mock_stats = mock.AsyncMock()
    mock_stats_ctx.return_value = mock_stats

    # Call task
    await async_count_active_users()

    # Expected
    today = datetime.now(timezone.utc)
    reading = Reading(
        datetime=datetime(today.year, today.month, today.day),
        subject=ReadingSubject.ACTIVE_USERS,
        value=99,
        unit="users",
    )

    # Assert result
    mock_users.count_active_users.assert_called_with()
    mock_stats.upsert.assert_called_with(reading)
