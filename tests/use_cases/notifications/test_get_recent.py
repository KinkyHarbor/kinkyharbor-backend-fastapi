'''Unit tests for Get Recent Notifications usecase'''

from unittest import mock

import pytest

from harbor.domain.notification import Notification
from harbor.repository.base import NotificationRepo
from harbor.use_cases.notifications import get_recent as uc_recent


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a get historic notifications request'''
    return uc_recent.GetRecentRequest(
        user_id='5e7f656765f1b64f3f7f6900',
    )


@pytest.fixture(name="notifs")
def fixture_notifs():
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


@pytest.mark.asyncio
async def test_success(uc_req, notifs):
    '''Should return lists of historic notifications'''
    # Create mocks
    notif_repo = mock.Mock(NotificationRepo)
    notif_repo.get_recent.return_value = notifs

    # Call usecase
    uc = uc_recent.GetRecentUsecase(notif_repo)
    result = await uc.execute(uc_req)

    # Assert results
    notif_repo.get_recent.assert_called_with('5e7f656765f1b64f3f7f6900')
    assert result == notifs
