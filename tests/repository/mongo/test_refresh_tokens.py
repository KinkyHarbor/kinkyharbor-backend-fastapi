'''Test cases for crud refresh tokens module'''
# pylint: disable=unused-argument

import uuid
from typing import Dict

import pytest

from harbor.domain.notification import Notification
from harbor.helpers.settings import get_settings
from harbor.repository.mongo.refresh_tokens import create_repo


def notif_to_assert_dict(notif: Notification) -> Dict:
    '''Convert Notification to assertable dict'''
    return notif.dict(exclude={'id', 'created_on'})


@pytest.fixture(name='repo')
async def fixture_repo(monkeypatch, event_loop):
    '''Returns a temporary refresh tokens repo for testing'''
    appendix = str(uuid.uuid4()).replace('-', '')[:10]
    monkeypatch.setenv("MONGO_DATABASE", f"test-kh-refresh-tokens-{appendix}")
    get_settings.cache_clear()
    repo = await create_repo()
    yield repo
    repo.client.drop_database(repo.db)


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_refresh_token_roundtrip(repo):
    '''Tests to create and replace a refresh token'''
    # Create and replace tokens
    user_id = '5e7f656765f1b64f3f7f6900'
    token = await repo.create_token(user_id)

    invalid_secret = token.copy()
    invalid_secret.secret = 'invalid'
    invalid_secret_result = await repo.replace_token(invalid_secret)

    invalid_user_id = token.copy()
    invalid_user_id.user_id = '5e7f656765f1b64f3f7f6999'
    invalid_user_id_result = await repo.replace_token(invalid_user_id)

    token2 = await repo.replace_token(token)
    invalid_token = await repo.replace_token(token)

    # Assert results
    assert token.user_id == user_id
    assert len(token.secret) > 0
    assert invalid_secret_result is None
    assert invalid_user_id_result is None
    assert token.user_id == token2.user_id
    assert len(token2.secret) > 0
    assert token.secret != token2.secret
    assert invalid_token is None
