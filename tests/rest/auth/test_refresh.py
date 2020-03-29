'''Unit tests for Auth Password Reset rest api'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.domain.token import AccessRefreshTokens
from harbor.repository.base import get_repos
from harbor.use_cases.auth import token_refresh as uc_refresh


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


# =======================================
# =            /auth/refresh/           =
# =======================================

@pytest.fixture(name="json_refresh_req")
def fixture_json_pw_exec_req():
    '''Returns expected request to execute refresh usecase'''
    return {
        'refresh_token': '5e7f656765f1b64f3f7f69f2:-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM'
    }


@pytest.fixture(name="uc_refresh_req")
def fixture_uc_pw_exec_req(json_refresh_req):
    '''Returns expected request to execute refresh usecase'''
    return uc_refresh.TokenRefreshRequest(**json_refresh_req)


@mock.patch.object(uc_refresh.TokenRefreshUseCase, 'execute')
def test_success_valid_token(uc_exec, client, json_refresh_req, uc_refresh_req):
    '''Should return new access and refresh token'''
    # Mock use case response
    expected = AccessRefreshTokens(
        access_token='TestAccessToken',
        refresh_token='TestRefreshToken',
    )
    uc_exec.return_value = expected

    # Send test request
    response = client.post("/auth/refresh/", json=json_refresh_req)

    # Assert results
    uc_exec.assert_called_with(uc_refresh_req)
    assert response.url == 'http://testserver/auth/refresh/'
    assert response.json() == expected.dict()
    assert response.status_code == 200


@mock.patch.object(uc_refresh.TokenRefreshUseCase, 'execute')
def test_fail_invalid_token(uc_exec, client, json_refresh_req, uc_refresh_req):
    '''Should return a invalid token error'''
    # Mock use case response
    uc_exec.side_effect = uc_refresh.InvalidTokenError

    # Send test request
    response = client.post("/auth/refresh/", json=json_refresh_req)

    # Assert results
    uc_exec.assert_called_with(uc_refresh_req)
    assert response.url == 'http://testserver/auth/refresh/'
    assert 'invalid' in response.json().get('msg').lower()
    assert response.status_code == 401
