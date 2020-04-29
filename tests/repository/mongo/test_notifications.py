'''Test cases for crud user module'''
# pylint: disable=unused-argument

import uuid
from datetime import timedelta
from typing import Dict

import pytest

from harbor.domain.notification import Notification
from harbor.helpers.settings import get_settings
from harbor.repository.mongo.notifications import create_repo


def notif_to_assert_dict(notif: Notification) -> Dict:
    '''Convert Notification to assertable dict'''
    return notif.dict(exclude={'id', 'created_on'})


@pytest.fixture(name='notif_repo')
async def fixture_notif_repo(monkeypatch, event_loop):
    '''Returns a temporary notification repo for testing'''
    appendix = str(uuid.uuid4()).replace('-', '')[:10]
    monkeypatch.setenv("MONGO_DATABASE", f"test-kh-notificatons-{appendix}")
    get_settings.cache_clear()
    repo = await create_repo()
    yield repo
    repo.client.drop_database(repo.db)


@pytest.mark.mongo
@pytest.mark.asyncio
@pytest.mark.parametrize('days,is_read,expected_len', [
    (1, False, 1),
    (1, True, 1),
    (7, False, 1),
    (7, True, 0),  # Notification is 7 days and 1 second old
    (8, False, 1),
    (8, True, 0),
    (365, False, 1),
    (365, True, 0),
])
async def test_recent_notifications(notif_repo, days, is_read, expected_len):
    '''Tests to register and retrieve a notification'''
    notif = Notification(
        user_id='5e7f656765f1b64f3f7f6900',
        title='Test notif 1',
        description='Test notif desc 1',
        icon='https://kh.test/icon1',
        link='https://kh.test/link1',
        is_read=is_read,
    )
    notif.created_on -= timedelta(days=days)
    await notif_repo.add(notif)

    result_notifs = await notif_repo.get_recent('5e7f656765f1b64f3f7f6900')

    assert len(result_notifs) == expected_len
    if expected_len > 0:
        notif_dict = notif_to_assert_dict(notif)
        result_dict = notif_to_assert_dict(result_notifs[0])
        assert notif_dict == result_dict


@pytest.mark.mongo
@pytest.mark.asyncio
@pytest.mark.parametrize('is_read', [True, False])
async def test_historic_notifications(notif_repo, is_read):
    '''Tests to register and retrieve a notification'''
    # Build test notification
    notif = Notification(
        user_id='5e7f656765f1b64f3f7f6900',
        title='Test notif 1',
        description='Test notif desc 1',
        icon='https://kh.test/icon1',
        link='https://kh.test/link1',
        is_read=is_read
    )

    # Store test notifications in database
    notifs = []
    for days in range(90, -1, -30):
        notif_copy = notif.copy()
        notif_copy.created_on -= timedelta(days=days)
        await notif_repo.add(notif_copy)
        notifs.append(notif_copy)

    # Call repository
    days10 = notif.created_on - timedelta(days=10)
    days70 = notif.created_on - timedelta(days=70)
    result_notifs = await notif_repo.get_historic('5e7f656765f1b64f3f7f6900', days70, days10)

    # Assert results
    expected_notifs = notifs[1:3]
    assert len(result_notifs) == 2
    for i in range(2):
        notif_dict = notif_to_assert_dict(expected_notifs[i])
        result_dict = notif_to_assert_dict(result_notifs[i])
        assert notif_dict == result_dict
