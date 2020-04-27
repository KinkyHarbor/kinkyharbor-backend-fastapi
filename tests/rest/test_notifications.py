'''Unit tests for Notifications rest api'''
# pylint: disable=unused-argument

from datetime import datetime, timezone
from typing import List
from unittest import mock

import pytest
from starlette.testclient import TestClient
from pydantic import parse_obj_as

from harbor.app import app
from harbor.domain.notification import Notification
from harbor.domain.token import AccessTokenData
from harbor.repository.base import get_repos
from harbor.rest.auth.base import validate_access_token
from harbor.use_cases.notifications import (
    get_recent as uc_recent,
    get_historic as uc_historic,
    mark_as_read as uc_mark,
)


def get_repos_override():
    '''Overrides repositories'''
    repos = mock.MagicMock()
    repos.__getitem__.side_effect = mock.Mock
    return repos


def validate_access_token_override():
    '''Overrides access token validation'''
    return AccessTokenData(user_id='5e7f656765f1b64f3f7f6900')


@pytest.fixture(name="client")
def fixture_client():
    '''Returns a test client'''
    app.dependency_overrides[get_repos] = get_repos_override
    app.dependency_overrides[validate_access_token] = validate_access_token_override
    return TestClient(app)


@pytest.fixture(name="notifications")
def fixture_notifications():
    '''Returns two test notifications'''
    return [
        Notification(
            user_id='5e7f656765f1b64f3f7f6900',
            title='Test notif 1',
            description='Test notif desc 1',
            icon='https://kh.test/icon1',
            link='https://kh.test/link1',
        ),
        Notification(
            user_id='5e7f656765f1b64f3f7f6900',
            title='Test notif 2',
            description='Test notif desc 2',
            is_read=True,
            icon='https://kh.test/icon2',
            link='https://kh.test/link2',
        ),
    ]


# =======================================
# =         GET /notifications/         =
# =======================================

@mock.patch.object(uc_recent.GetRecentUsecase, 'execute')
def test_success_get_recent(uc_recent_mock, client, notifications, freezer):
    '''Should return recent notifications'''
    # Mock use case response
    uc_recent_mock.return_value = notifications

    # Send test request
    response = client.get("/notifications/")

    # Assert results
    uc_req = uc_recent.GetRecentRequest(
        user_id='5e7f656765f1b64f3f7f6900'
    )
    uc_recent_mock.assert_called_with(uc_req)
    assert response.url == 'http://testserver/notifications/'
    assert parse_obj_as(List[Notification], response.json()) == notifications
    assert response.status_code == 200


# =======================================
# =  POST /notifications/get-historic/  =
# =======================================

@mock.patch.object(uc_historic.GetHistoricUsecase, 'execute')
def test_success_get_historic(uc_historic_mock, client, notifications, freezer):
    '''Should return historic notifications'''
    # Mock use case response
    uc_historic_mock.return_value = notifications

    # Send test request
    response = client.post("/notifications/get-historic/", json={
        "from": "2020-03-26T19:39:36.006Z",
        "to": "2020-04-26T19:39:36.006Z",
    })

    # Assert results
    uc_req = uc_historic.GetHistoricRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        from_=datetime(2020, 3, 26, 19, 39, 36, 6000, timezone.utc),
        to=datetime(2020, 4, 26, 19, 39, 36, 6000, timezone.utc),
    )
    uc_historic_mock.assert_called_with(uc_req)
    assert response.url == 'http://testserver/notifications/get-historic/'
    assert parse_obj_as(List[Notification], response.json()) == notifications
    assert response.status_code == 200


@mock.patch.object(uc_historic.GetHistoricUsecase, 'execute')
def test_fail_get_historic_max_time_range_exc(uc_historic_mock, client, notifications, freezer):
    '''Should return max time range exceeded error'''
    # Mock use case response
    uc_historic_mock.side_effect = uc_historic.MaxTimeRangeExceeded

    # Send test request
    response = client.post("/notifications/get-historic/", json={
        "from": "2019-04-26T19:39:36.006Z",
        "to": "2020-04-26T19:39:36.006Z",
    })

    # Assert results
    uc_req = uc_historic.GetHistoricRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        from_=datetime(2019, 4, 26, 19, 39, 36, 6000, timezone.utc),
        to=datetime(2020, 4, 26, 19, 39, 36, 6000, timezone.utc),
    )
    uc_historic_mock.assert_called_with(uc_req)
    assert response.url == 'http://testserver/notifications/get-historic/'
    assert response.json()['code'] == 'max_time_range_exceeded'
    assert response.status_code == 400


# =======================================
# =  POST /notifications/mark-as-read/  =
# =======================================

@mock.patch.object(uc_mark.MarkAsReadUsecase, 'execute')
def test_success_mark_as_read(uc_mark_mock, client, notifications, freezer):
    '''Should mark notifications as read'''
    # Mock use case response
    uc_mark_mock.return_value = uc_mark.MarkAsReadResponse(
        count_updated=2,
    )

    # Send test request
    response = client.post("/notifications/mark-as-read/", json={
        "notification_ids": [
            "5ea5d4cb8322e417540fb555",
            "5ea5d4cb8322e417540fb666",
        ],
    })

    # Assert results
    uc_req = uc_mark.MarkAsReadRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        notification_ids=[
            "5ea5d4cb8322e417540fb555",
            "5ea5d4cb8322e417540fb666",
        ],
        is_read=True,
    )
    uc_mark_mock.assert_called_with(uc_req)
    assert response.url == 'http://testserver/notifications/mark-as-read/'
    assert response.json()['count_updated'] == 2
    assert response.status_code == 200


@mock.patch.object(uc_mark.MarkAsReadUsecase, 'execute')
def test_success_mark_as_unread(uc_mark_mock, client, notifications, freezer):
    '''Should mark notifications as unread'''
    # Mock use case response
    uc_mark_mock.return_value = uc_mark.MarkAsReadResponse(
        count_updated=2,
    )

    # Send test request
    response = client.post("/notifications/mark-as-read/", json={
        "notification_ids": [
            "5ea5d4cb8322e417540fb555",
            "5ea5d4cb8322e417540fb666",
        ],
        "unread": True,
    })

    # Assert results
    uc_req = uc_mark.MarkAsReadRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        notification_ids=[
            "5ea5d4cb8322e417540fb555",
            "5ea5d4cb8322e417540fb666",
        ],
        is_read=False,
    )
    uc_mark_mock.assert_called_with(uc_req)
    assert response.url == 'http://testserver/notifications/mark-as-read/'
    assert response.json()['count_updated'] == 2
    assert response.status_code == 200
