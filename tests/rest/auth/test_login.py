'''Unit tests for Auth Login rest api'''

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


@pytest.fixture(name="uc_req")
def fixture_uc_req():
    '''Returns expected request to provided usecase'''
    return uc.LoginRequest(
        login='TestUser',
        password='TestPassword',
    )


# ================================
# =         /auth/login/         =
# ================================

@mock.patch.object(uc.LoginUseCase, 'execute')
def test_success_login(uc_exec, client, uc_req):
    '''Should return an access and refresh token'''
    # Mock use case response
    uc_exec.return_value = uc.LoginResponse(
        access_token='TestAccessToken',
        refresh_token='TestRefreshToken',
    )

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {
        'access_token': 'TestAccessToken',
        'refresh_token': 'TestRefreshToken',
    }
    assert response.status_code == 200


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_fail_login_invalid_creds(uc_exec, client, uc_req):
    '''Should return an invalid credentials error'''
    # Mock use case response
    uc_exec.side_effect = uc.InvalidCredsError

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {'msg': 'Incorrect username or password'}
    assert response.status_code == 401


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_fail_login_user_locked(uc_exec, client, uc_req):
    '''Should return a user locked error'''
    # Mock use case response
    uc_exec.side_effect = uc.UserLockedError

    # Send test request
    response = client.post("/auth/login/", json={
        'login': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/'
    assert response.json() == {'msg': 'User is locked'}
    assert response.status_code == 401


# ================================
# =      /auth/login/token/      =
# ================================

@mock.patch.object(uc.LoginUseCase, 'execute')
def test_success_login_token(uc_exec, client, uc_req):
    '''Should return an access and refresh token'''
    # Mock use case response
    uc_exec.return_value = uc.LoginResponse(
        access_token='TestAccessToken',
        refresh_token='TestRefreshToken',
    )

    # Send test request
    response = client.post("/auth/login/token/", data={
        'username': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/token/'
    assert response.json() == {
        'token': 'TestAccessToken',
        'token_type': 'bearer',
    }
    assert response.status_code == 200


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_fail_login_token_invalid_creds(uc_exec, client, uc_req):
    '''Should return an invalid credentials error'''
    # Mock use case response
    uc_exec.side_effect = uc.InvalidCredsError

    # Send test request
    response = client.post("/auth/login/token/", data={
        'username': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/token/'
    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == 401


@mock.patch.object(uc.LoginUseCase, 'execute')
def test_fail_login_user_token_locked(uc_exec, client, uc_req):
    '''Should return a user locked error'''
    # Mock use case response
    uc_exec.side_effect = uc.UserLockedError

    # Send test request
    response = client.post("/auth/login/token/", data={
        'username': 'TestUser',
        'password': 'TestPassword',
    })

    # Assert results
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/token/'
    assert response.json() == {'detail': 'User is locked'}
    assert response.status_code == 401
