'''Test cases for crud verification tokens module'''
# pylint: disable=unused-argument

import uuid

import pytest

from harbor.domain.token import TokenVerifyRequest, VerificationPurposeEnum as VerifPur
from harbor.helpers.settings import get_settings
from harbor.repository.mongo.verif_tokens import create_repo


@pytest.fixture(name='repo')
async def fixture_repo(monkeypatch, event_loop):
    '''Returns a temporary stats repo for testing'''
    appendix = str(uuid.uuid4()).replace('-', '')[:10]
    monkeypatch.setenv("MONGO_DATABASE", f"test-kh-verif-tokens-{appendix}")
    get_settings.cache_clear()
    repo = await create_repo()
    yield repo
    repo.client.drop_database(repo.db)


@pytest.fixture(name='user_id')
async def fixture_user_id():
    '''Returns a user ID'''
    return '5e7f656765f1b64f3f7f6900'


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_verif_token_roundtrip(repo, user_id):
    '''Tests to create and verify a token'''
    # Create token and request
    token = await repo.create_verif_token(user_id, VerifPur.REGISTER)
    req = TokenVerifyRequest(**token.dict())

    # Validate token
    result = await repo.verify_verif_token(req)
    assert result == token

    # Validate same token
    result = await repo.verify_verif_token(req)
    assert result is None


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_verif_token_not_owned_by_user(repo, user_id):
    '''Tests if verification token is kept intact if not owned by user'''
    # Create token and request
    token = await repo.create_verif_token(user_id, VerifPur.REGISTER)
    req = TokenVerifyRequest(**token.dict())

    # Validate token
    req2 = req.copy()
    req2.user_id = req2.user_id[:-2] + "99"
    result = await repo.verify_verif_token(req2)
    assert result is None

    # Validate same token
    result = await repo.verify_verif_token(req)
    assert result == token


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_verif_token_invalid_purpose(repo, user_id):
    '''Tests if token is deleted if verified for wrong purpose'''
    # Create token and request
    token = await repo.create_verif_token(user_id, VerifPur.REGISTER)
    req = TokenVerifyRequest(**token.dict())
    req.purpose = VerifPur.RESET_PASSWORD

    # Validate token
    result = await repo.verify_verif_token(req)
    assert result is None

    # Validate same token
    result = await repo.verify_verif_token(req)
    assert result is None
