'''Test cases for crud user module'''
# pylint: disable=unused-argument

import uuid
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
async def test_notifications(notif_repo):
    '''Tests to register and retrieve a new user'''
    notif = Notification(
        user_id='5e7f656765f1b64f3f7f6900',
        title='Test notif 1',
        description='Test notif desc 1',
        icon='https://kh.test/icon1',
        link='https://kh.test/link1',
    )
    await notif_repo.add(notif)

    result_notifs = await notif_repo.get_recent('5e7f656765f1b64f3f7f6900')

    assert len(result_notifs) == 1
    notif_dict = notif_to_assert_dict(notif)
    result_dict = notif_to_assert_dict(result_notifs[0])
    assert notif_dict == result_dict
