'''Unit tests for Search Generic usecase'''

from unittest import mock

import pytest

from harbor.domain.user import BaseUser
from harbor.repository.base import UserRepo
from harbor.use_cases.search import generic as uc_search_gen


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a generic search request'''
    return uc_search_gen.GenericSearchRequest(
        query='test',
        user_id='507f1f77bcf86cd799439010',
    )


@pytest.fixture(name='test_users')
def fixture_test_users():
    '''Returns a list of users'''
    return [
        BaseUser(
            id='507f1f77bcf86cd799439011',
            display_name='TestUser1',
        ),
        BaseUser(
            id='507f1f77bcf86cd799439012',
            display_name='TestUser2',
        ),
    ]


@pytest.mark.asyncio
async def test_success(uc_req, test_users):
    '''Should return lists of users, groups, pages and events'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_search.return_value = test_users

    # Call usecase
    uc = uc_search_gen.GenericSearchUseCase(user_repo)
    result = await uc.execute(uc_req)

    # Assert results
    user_repo.get_search.assert_called_with('507f1f77bcf86cd799439010', 'test')
    assert result.users == test_users
    assert result.groups == []
    assert result.pages == []
    assert result.events == []
