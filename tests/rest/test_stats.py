'''Unit tests for Stats rest api'''

from datetime import date
from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.domain import stats
from harbor.repository.base import get_repos
from harbor.use_cases.stats import get_active_user_count as uc


def get_repos_override():
    '''Overrides repositories'''
    repos = mock.MagicMock()
    repos.__getitem__.side_effect = mock.Mock
    return repos


@pytest.fixture(name="client")
def fixture_client():
    '''Returns a test client'''
    client = TestClient(app)
    app.dependency_overrides[get_repos] = get_repos_override
    return client


# =======================================
# =         /stats/active-users         =
# =======================================

@mock.patch.object(uc.GetActiveUserCountUsecase, 'execute')
def test_success(uc_count, client):
    '''Should return active user count'''
    # Mock use case response
    uc_count.return_value = uc.GetActiveUserCountResponse(
        now=50,
        history=stats.ReadingAggregation(
            subject=stats.ReadingSubject.ACTIVE_USERS,
            timespan=stats.ReadingAggregationTimespan.MONTH,
            operation=stats.ReadingAggregationOperation.AVERAGE,
            values={
                date(2020, 4, 1): 49,
                date(2020, 3, 1): 37,
            }
        )
    )

    # Send test request
    response = client.get("/stats/active-users/")

    # Assert results
    uc_count.assert_called_with()
    assert response.url == 'http://testserver/stats/active-users'
    assert response.json() == {
        'now': 50,
        'history': {
            '2020-04-01': 49,
            '2020-03-01': 37,
        },
    }
    assert response.status_code == 200
