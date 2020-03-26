'''Test generic behavior'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.repository.base import get_repos
from harbor.use_cases.auth import login as uc


def get_repos_override():
    '''Overrides repositories'''
    repos = mock.MagicMock()
    repos.__getitem__.side_effect = mock.Mock
    return repos


@pytest.fixture(name="client")
def fixture_client():
    '''Returns a test client'''
    client = TestClient(app)
    app.dependency_overrides[get_repos] = get_repos_override
    return client


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_login_success(repo_exc, client):
    '''Should return an access and refresh token'''
    # Mock use case response
    repo_exc.return_value = uc.LoginResponse(
        access_token='TestAccessToken',
        refresh_token='TestRefreshToken',
    )

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    assert response.status_code == 200
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {
        'access_token': 'TestAccessToken',
        'refresh_token': 'TestRefreshToken',
    }


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_login_invalid_creds_fail(repo_exc, client):
    '''Should return an invalid credentials error'''
    # Mock use case response
    repo_exc.side_effect = uc.InvalidCredsError

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    assert response.status_code == 401
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {'msg': 'Incorrect username or password'}


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_login_user_locked_fail(repo_exc, client):
    '''Should return a user locked error'''
    # Mock use case response
    repo_exc.side_effect = uc.UserLockedError

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    assert response.status_code == 401
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {'msg': 'User is locked'}
