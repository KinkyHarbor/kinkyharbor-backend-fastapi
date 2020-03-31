'''Unit tests for Auth Password Reset rest api'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.repository.base import get_repos
from harbor.use_cases.auth import (
    reset_password_req as uc_pw_req,
    reset_password_exec as uc_pw_exec,
)


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
# = /auth/login/request-password-reset/ =
# =======================================

@mock.patch.object(uc_pw_req.RequestPasswordResetUseCase, 'execute')
def test_success_request_password_reset(uc_exec, client):
    '''Should check user and send reset link'''
    # Send test request
    response = client.post("/auth/login/request-password-reset/", json={
        'email': 'user@kh.test'
    })

    # Assert results
    uc_req = uc_pw_req.RequestPasswordResetRequest(email='user@kh.test')
    uc_exec.assert_called_with(uc_req)
    assert response.url == 'http://testserver/auth/login/request-password-reset/'
    assert 'mail sent' in response.json().get('msg')
    assert response.status_code == 200


# =======================================
# =     /auth/login/password-reset/     =
# =======================================

@pytest.fixture(name="json_pw_exec_req")
def fixture_json_pw_exec_req():
    '''Returns expected request to execute password reset usecase'''
    return {
        'user_id': '5e7f656765f1b64f3f7f69f2',
        'token': '-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
        'password': 'VeryStrongTestPassword',
    }


@pytest.fixture(name="uc_pw_exec_req")
def fixture_uc_pw_exec_req(json_pw_exec_req):
    '''Returns expected request to execute password reset usecase'''
    return uc_pw_exec.ExecPasswordResetRequest(**json_pw_exec_req)


@mock.patch.object(uc_pw_exec.ExecResetPasswordUseCase, 'execute')
def test_success_exec_password_reset_updated(uc_exec, client, json_pw_exec_req, uc_pw_exec_req):
    '''Should check token and reset password'''
    # Mock use case response
    uc_exec.return_value = uc_pw_exec.ExecResetPasswordResponse.UPDATED

    # Send test request
    response = client.post("/auth/login/password-reset/",
                           json=json_pw_exec_req)

    # Assert results
    uc_exec.assert_called_with(uc_pw_exec_req)
    assert response.url == 'http://testserver/auth/login/password-reset/'
    assert 'updated' in response.json().get('msg')
    assert 'verified' not in response.json().get('msg')
    assert response.status_code == 200


@mock.patch.object(uc_pw_exec.ExecResetPasswordUseCase, 'execute')
def test_success_exec_password_reset_verified(uc_exec, client, json_pw_exec_req, uc_pw_exec_req):
    '''Should check token, reset password and verify account'''
    # Mock use case response
    uc_exec.return_value = uc_pw_exec.ExecResetPasswordResponse.UPDATED_AND_VERIFIED

    # Send test request
    response = client.post("/auth/login/password-reset/",
                           json=json_pw_exec_req)

    # Assert results
    uc_exec.assert_called_with(uc_pw_exec_req)
    assert response.url == 'http://testserver/auth/login/password-reset/'
    assert 'updated' in response.json().get('msg')
    assert 'verified' in response.json().get('msg')
    assert response.status_code == 200


@mock.patch.object(uc_pw_exec.ExecResetPasswordUseCase, 'execute')
def test_fail_exec_password_reset_invalid_token(uc_exec, client, json_pw_exec_req, uc_pw_exec_req):
    '''Should return a invalid token error'''
    # Mock use case response
    uc_exec.side_effect = uc_pw_exec.InvalidTokenError

    # Send test request
    response = client.post("/auth/login/password-reset/",
                           json=json_pw_exec_req)

    # Assert results
    uc_exec.assert_called_with(uc_pw_exec_req)
    assert response.url == 'http://testserver/auth/login/password-reset/'
    assert 'invalid' in response.json().get('msg')
    assert response.status_code == 400
