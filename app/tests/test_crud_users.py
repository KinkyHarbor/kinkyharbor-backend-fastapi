'''Test cases for crud user module'''

import pytest

from core import settings
from crud import users
from models.user import RegisterUser


settings.MONGO_DATABASE = f'{settings.MONGO_DATABASE}_test'


@pytest.mark.asyncio
async def test_register_new_user():
    '''Tests to register and retrieve a new user'''
    user = RegisterUser(
        username='pytest',
        email='test@example.com',
        password='test'
    )

    result = await users.register(user)

    saved_user = await users.get(result.inserted_id)

    # pylint: disable=maybe-no-member
    assert user.username == saved_user.username
    assert user.email == saved_user.email
