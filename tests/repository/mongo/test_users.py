'''Test cases for crud users module'''
# pylint: disable=unused-argument

import uuid
from datetime import datetime, timezone, timedelta

import pytest

from harbor.domain.user import User, UserWithPassword, UserFlags, UserInfo
from harbor.helpers.settings import get_settings
from harbor.repository.mongo.users import create_repo, UsernameTakenError, EmailTakenError


@pytest.fixture(name='repo')
async def fixture_repo(monkeypatch, event_loop):
    '''Returns a temporary stats repo for testing'''
    appendix = str(uuid.uuid4()).replace('-', '')[:10]
    monkeypatch.setenv("MONGO_DATABASE", f"test-kh-users-{appendix}")
    get_settings.cache_clear()
    repo = await create_repo()
    yield repo
    repo.client.drop_database(repo.db)


async def add_user(repo, appendix) -> User:
    '''Insert a user in the database'''
    return await repo.add(
        display_name=f"TestUser{appendix}",
        email=f"user{appendix}@kh.test",
        password_hash=f"test-password-hash{appendix}",
    )


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_roundtrip(repo):
    '''Tests to add and fetch a user'''
    # Insert users
    user = await add_user(repo, "")
    await add_user(repo, "2")

    # Fetch user by ID
    result = await repo.get(user.id)
    assert result == user

    # Expected result for by login
    expected = UserWithPassword(
        password_hash="test-password-hash",
        **user.dict(),
    )

    # Fetch user by login (Username)
    result = await repo.get_by_login("testuser")
    assert result == expected

    # Fetch user by login (Email)
    result = await repo.get_by_login("user@kh.test")
    assert result == expected

    # Fetch user by username
    result = await repo.get_by_username("testuser")
    assert result == user


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_verify_and_search(repo):
    '''Tests to verify a user and search in users'''
    # Insert users
    new_user = await add_user(repo, "")
    new_user2 = await add_user(repo, "2")
    new_user3 = await add_user(repo, "3")

    # Verify users
    user = await repo.set_flag(new_user.id, UserFlags.VERIFIED, True)
    expected = new_user.copy()
    expected.is_verified = True
    assert expected == user

    user2 = await repo.set_flag(new_user2.id, UserFlags.VERIFIED, True)
    expected2 = new_user2.copy()
    expected2.is_verified = True
    assert expected2 == user2

    # Search users with own user
    result = await repo.get_search(new_user.id, "test")
    result_user_ids = [user.id for user in result]
    assert len(result) == 1
    assert new_user.id not in result_user_ids
    assert new_user2.id in result_user_ids
    assert new_user3.id not in result_user_ids

    # Search users with other user
    result = await repo.get_search(new_user3.id, "test")
    result_user_ids = [user.id for user in result]
    assert len(result) == 2
    assert new_user.id in result_user_ids
    assert new_user2.id in result_user_ids
    assert new_user3.id not in result_user_ids


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_search_limit(repo):
    '''Tests limit argument of search in users'''
    # Insert users
    for i in range(10):
        user_a = await add_user(repo, f"A{i}")
        await repo.set_flag(user_a.id, UserFlags.VERIFIED, True)
        user_b = await add_user(repo, f"B{i}")
        await repo.set_flag(user_b.id, UserFlags.VERIFIED, True)

    # Search users
    result = await repo.get_search('5e7f656765f1b64f3f7f6900', "TeStUsErA", 5)
    assert len(result) == 5
    assert all(("testusera" in user.username for user in result))
    assert not any(("testuserb" in user.username for user in result))


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_active_count(repo):
    '''Tests counting of active users'''
    # Insert users
    for i in range(5):
        user = await add_user(repo, f"A{i}")
        await repo.update_last_login(user.id)
        await add_user(repo, f"B{i}")

    # Count active users
    result = await repo.count_active_users()
    assert result == 5


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_add_duplicate_username(repo):
    '''Tests error on duplicate usernames'''
    await repo.add(
        display_name="TestUser",
        email="user@kh.test",
        password_hash="test-password-hash",
    )
    with pytest.raises(UsernameTakenError):
        await repo.add(
            display_name="TestUser",
            email="user2@kh.test",
            password_hash="test-password-hash2",
        )


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_add_duplicate_email(repo):
    '''Tests error on duplicate email'''
    await repo.add(
        display_name="TestUser",
        email="user@kh.test",
        password_hash="test-password-hash",
    )
    with pytest.raises(EmailTakenError):
        await repo.add(
            display_name="TestUser2",
            email="user@kh.test",
            password_hash="test-password-hash2",
        )


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_set_password(repo):
    '''Tests setting a new password'''
    # Insert users
    new_user = await add_user(repo, "")
    new_user2 = await add_user(repo, "2")

    # Update password
    upd_user = await repo.set_password(new_user.id, "updated-password-hash")

    # Fetch users
    user = await repo.get_by_login("user@kh.test")
    user2 = await repo.get_by_login("user2@kh.test")

    # Assert results
    expected = UserWithPassword(
        password_hash="updated-password-hash",
        **new_user.dict(),
    )
    assert user == expected
    assert upd_user == new_user
    assert user2.password_hash == "test-password-hash2"
    assert User(**user2.dict()) == new_user2


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_set_info(repo):
    '''Tests updating info of a user'''
    # Insert users
    new_user = await add_user(repo, "")
    new_user2 = await add_user(repo, "2")

    # Update info at once
    upd_user = await repo.set_info(new_user.id, UserInfo(
        bio='test-bio',
        gender='test-gender',
    ))

    # Update info in parts
    # Second update should not overwrite the first one
    await repo.set_info(new_user2.id, UserInfo(
        bio='test-bio2',
    ))
    upd_user2 = await repo.set_info(new_user2.id, UserInfo(
        gender='test-gender2',
    ))

    # Assert results
    new_user.bio = 'test-bio'
    new_user.gender = 'test-gender'
    assert upd_user == new_user
    new_user2.bio = 'test-bio2'
    new_user2.gender = 'test-gender2'
    assert upd_user2 == new_user2


@pytest.mark.mongo
@pytest.mark.asyncio
async def test_user_update_last_login(repo):
    '''Tests updating the last login of the user'''
    user = await add_user(repo, "")
    await repo.update_last_login(user.id)
    user = await repo.get(user.id)
    now = datetime.now(timezone.utc)
    assert now - timedelta(minutes=1) < user.last_login < now
