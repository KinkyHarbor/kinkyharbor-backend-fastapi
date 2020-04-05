'''Unit tests for Search rest api'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.domain.token import AccessTokenData
from harbor.domain.user import BaseUser
from harbor.helpers.auth import validate_access_token
from harbor.repository.base import get_repos
from harbor.use_cases.search import generic as uc


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
    client = TestClient(app)
    app.dependency_overrides[get_repos] = get_repos_override
    app.dependency_overrides[validate_access_token] = validate_access_token_override
    return client


# =======================================
# =               /search/              =
# =======================================

@mock.patch.object(uc.GenericSearchUseCase, 'execute')
def test_success(uc_exec, client):
    '''Should return search results for users, groups, pages and events'''
    # Mock use case response
    user = BaseUser(
        id='5e7f656765f1b64f3f7f6999',
        display_name='TestUser1',
    )
    uc_exec.return_value = uc.GenericSearchResponse(
        users=[user],
        groups=[],
        pages=[],
        events=[],
    )

    # Send test request
    response = client.get("/search/?q=test")

    # Assert results
    uc_req = uc.GenericSearchRequest(
        query='test',
        user_id='5e7f656765f1b64f3f7f6900'
    )
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/search/?q=test'
    assert response.json() == {
        'users': [user.dict()],
        'groups': [],
        'pages': [],
        'events': [],
    }
    assert response.status_code == 200
