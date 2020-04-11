'''Unit tests for Users rest api'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.domain.token import AccessTokenData
from harbor.domain.user import User, UserRelation
from harbor.repository.base import get_repos
from harbor.rest.auth.base import validate_access_token
from harbor.use_cases.user import (
    profile_get as uc_get,
    profile_update as uc_upd,
)


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
# =            GET /users/me/           =
# =======================================

@mock.patch.object(uc_get.GetProfileUsercase, 'execute')
def test_success_get_profile_me(uc_exec, client):
    '''Should return user's profile'''
    # Mock use case response
    user = User(
        id='5e7f656765f1b64f3f7f6900',
        display_name='TestUser'
    )
    uc_exec.return_value = uc_get.GetProfileResponse(
        user=user,
        exposed_fields=['test-field'],
        relation=UserRelation.SELF,
    )

    # Send test request
    response = client.get("/users/me/")

    # Assert results
    uc_req = uc_get.GetProfileByIDRequest(
        requester='5e7f656765f1b64f3f7f6900',
        user_id='5e7f656765f1b64f3f7f6900',
    )
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/users/me/'
    assert response.json() == {
        'user': user.dict(),
        'exposed_fields': ['test-field'],
        'relation': 'SELF',
    }
    assert response.status_code == 200


# =======================================
# =           PATCH /users/me/          =
# =======================================

@pytest.fixture(name="json_upd_req")
def fixture_json_upd_req():
    '''Returns expected request to execute profile update usecase'''
    return {
        'bio': 'test-bio',
        'gender': 'test-gender',
    }


@pytest.fixture(name="uc_upd_req")
def fixture_uc_upd_req(json_upd_req):
    '''Returns expected request to execute profile update usecase'''
    return uc_upd.UpdateProfileRequest(
        user_id='5e7f656765f1b64f3f7f6900',
        **json_upd_req,
    )


@mock.patch.object(uc_upd.UpdateProfileUsercase, 'execute')
def test_success_update_profile(uc_exec, client, json_upd_req, uc_upd_req):
    '''Should update and return user's profile'''
    # Mock use case response
    expected = User(
        id='5e7f656765f1b64f3f7f6900',
        display_name='TestUser'
    )
    uc_exec.return_value = expected

    # Send test request
    response = client.patch("/users/me/", json=json_upd_req)

    # Assert results
    uc_exec.assert_called_with(uc_upd_req)
    assert response.url == 'http://testserver/users/me/'
    assert response.json() == expected.dict()
    assert response.status_code == 200


# =======================================
# =       GET /users/{username}/        =
# =======================================

@mock.patch.object(uc_get.GetProfileUsercase, 'execute')
def test_success_get_profile_username(uc_exec, client):
    '''Should return user's profile'''
    # Mock use case response
    user = User(
        id='5e7f656765f1b64f3f7f6999',
        display_name='Test-User'
    )
    uc_exec.return_value = uc_get.GetProfileResponse(
        user=user,
        exposed_fields=['test-field'],
        relation=UserRelation.FRIEND,
    )

    # Send test request
    response = client.get("/users/test-user/")

    # Assert results
    uc_req = uc_get.GetProfileByUsernameRequest(
        requester='5e7f656765f1b64f3f7f6900',
        username='test-user',
    )
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/users/test-user/'
    assert response.json() == {
        'user': user.dict(),
        'exposed_fields': ['test-field'],
        'relation': 'FRIEND',
    }
    assert response.status_code == 200


@mock.patch.object(uc_get.GetProfileUsercase, 'execute')
def test_fail_user_not_found(uc_exec, client):
    '''Should return UserNotFoundError'''
    # Mock use case response
    uc_exec.side_effect = uc_get.UserNotFoundError

    # Send test request
    response = client.get("/users/test-user/")

    # Assert results
    uc_req = uc_get.GetProfileByUsernameRequest(
        requester='5e7f656765f1b64f3f7f6900',
        username='test-user',
    )
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/users/test-user/'
    assert response.json()['code'] == 'not_found'
    assert response.status_code == 404
