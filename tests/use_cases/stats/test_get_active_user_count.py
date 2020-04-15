'''Unit tests for Stats: Get active user count usecase'''

from datetime import date, datetime, timezone
from unittest import mock

import pytest

from harbor.domain import stats
from harbor.repository.base import StatsRepo
from harbor.use_cases.stats import get_active_user_count as uc_count


@pytest.fixture(name='now')
def fixture_now():
    '''Returns a reading of active user counts'''
    return stats.Reading(
        datetime=datetime.now(timezone.utc),
        subject=stats.ReadingSubject.ACTIVE_USERS,
        value=50,
        unit="users",
    )


@pytest.fixture(name='history')
def fixture_history():
    '''Returns an aggregation of active user counts'''
    return stats.ReadingAggregation(
        subject=stats.ReadingSubject.ACTIVE_USERS,
        timespan=stats.ReadingAggregationTimespan.MONTH,
        operation=stats.ReadingAggregationOperation.AVERAGE,
        values={
            date(2020, 4, 1): 49,
            date(2020, 3, 1): 37,
        }
    )


@pytest.mark.asyncio
async def test_success(now, history):
    '''Should return present and historic active user counts'''
    # Create mocks
    stats_repo = mock.Mock(StatsRepo)
    stats_repo.get_latest.return_value = now
    stats_repo.get_by_month.return_value = history

    # Call usecase
    uc = uc_count.GetActiveUserCountUsecase(stats_repo)
    result = await uc.execute()

    # Assert results
    stats_repo.get_latest.assert_called_with(stats.ReadingSubject.ACTIVE_USERS)
    stats_repo.get_by_month.assert_called_with(
        stats.ReadingSubject.ACTIVE_USERS
    )
    assert result.now == now.value
    assert result.history == history
