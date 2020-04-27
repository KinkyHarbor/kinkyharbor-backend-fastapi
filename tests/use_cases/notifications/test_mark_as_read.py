'''Unit tests for Mark Notification As Read usecase'''

from unittest import mock

import pytest

from harbor.repository.base import NotificationRepo
from harbor.use_cases.notifications import mark_as_read as uc_mark


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a mark notification as read request'''
    return uc_mark.MarkAsReadRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        notification_ids=[
            '5e7f656765f1b64f3f7f6911',
            '5e7f656765f1b64f3f7f6922',
        ],
        is_read=True,
    )


@pytest.fixture(name='uc_res')
def fixture_uc_res():
    '''Returns a mark notification as read response'''
    return uc_mark.MarkAsReadResponse(
        count_updated=2,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('is_read', [True, False])
async def test_success(uc_req, uc_res, is_read):
    '''Should return count of updated notifications'''
    # Create mocks
    notif_repo = mock.Mock(NotificationRepo)
    notif_repo.set_read.return_value = 2

    # Call usecase
    uc = uc_mark.MarkAsReadUsecase(notif_repo)
    uc_req.is_read = is_read
    result = await uc.execute(uc_req)

    # Assert results
    notif_repo.set_read.assert_called_with(
        '5e7f656765f1b64f3f7f6900',
        [
            '5e7f656765f1b64f3f7f6911',
            '5e7f656765f1b64f3f7f6922',
        ],
        is_read)
    assert result == uc_res
