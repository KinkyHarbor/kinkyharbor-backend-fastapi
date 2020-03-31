'''Unit tests for Auth Register rest api'''

from unittest import mock

import pytest
from starlette.testclient import TestClient

from harbor.app import app
from harbor.repository.base import get_repos
from harbor.use_cases.auth import (
    register as uc_reg,
    register_verify as uc_ver,
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
# =           /auth/register/           =
# =======================================

@pytest.fixture(name="json_reg_req")
def fixture_json_reg_req():
    '''Returns expected request to execute register usecase'''
    return {
        'username': 'TestUser',
        'email': 'user@kh.test',
        'password': 'VeryStrongTestPassword',
        'isAdult': True,
        'acceptPrivacyAndTerms': True,
    }


@pytest.fixture(name="uc_reg_req")
def fixture_uc_reg_req(json_reg_req):
    '''Returns expected request to execute register usecase'''
    return uc_reg.RegisterRequest(
        display_name=json_reg_req['username'],
        is_adult=json_reg_req['isAdult'],
        accept_privacy_and_terms=json_reg_req['acceptPrivacyAndTerms'],
        **json_reg_req,
    )


@mock.patch.object(uc_reg.RegisterUseCase, 'execute')
def test_success_register(uc_exec, client, json_reg_req, uc_reg_req):
    '''Should register a new user and send verification mail'''
    # Send test request
    response = client.post("/auth/register/", json=json_reg_req)

    # Assert results
    uc_exec.assert_called_with(uc_reg_req)
    assert response.url == 'http://testserver/auth/register/'
    assert 'success' in response.json().get('msg').lower()
    assert response.status_code == 200


@mock.patch.object(uc_reg.RegisterUseCase, 'execute')
def test_fail_register_username_reserved(uc_exec, client, json_reg_req, uc_reg_req):
    '''Should return UsernameReserved error'''
    # Setup usecase mock
    uc_exec.side_effect = uc_reg.UsernameReservedError

    # Send test request
    response = client.post("/auth/register/", json=json_reg_req)

    # Assert results
    uc_exec.assert_called_with(uc_reg_req)
    assert response.url == 'http://testserver/auth/register/'
    assert 'reserved' in response.json().get('msg').lower()
    assert response.status_code == 400


@mock.patch.object(uc_reg.RegisterUseCase, 'execute')
def test_fail_register_username_taken(uc_exec, client, json_reg_req, uc_reg_req):
    '''Should return UsernameTaken error'''
    # Setup usecase mock
    uc_exec.side_effect = uc_reg.UsernameTakenError

    # Send test request
    response = client.post("/auth/register/", json=json_reg_req)

    # Assert results
    uc_exec.assert_called_with(uc_reg_req)
    assert response.url == 'http://testserver/auth/register/'
    assert 'taken' in response.json().get('msg').lower()
    assert response.status_code == 409


# =======================================
# =        /auth/register/verify/       =
# =======================================

@pytest.fixture(name="json_ver_req")
def fixture_json_ver_req():
    '''Returns expected request to execute register verification usecase'''
    return {
        'token': '-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
    }


@pytest.fixture(name="uc_ver_req")
def fixture_uc_ver_req(json_ver_req):
    '''Returns expected request to execute register verification usecase'''
    return uc_ver.RegisterVerifyRequest(secret=json_ver_req['token'])


@mock.patch.object(uc_ver.RegisterVerifyUseCase, 'execute')
def test_success_verify(uc_exec, client, json_ver_req, uc_ver_req):
    '''Should verify a user's registration'''
    # Send test request
    response = client.post("/auth/register/verify/", json=json_ver_req)

    # Assert results
    uc_exec.assert_called_with(uc_ver_req)
    assert response.url == 'http://testserver/auth/register/verify/'
    assert 'verified' in response.json().get('msg').lower()
    assert response.status_code == 200


@mock.patch.object(uc_ver.RegisterVerifyUseCase, 'execute')
def test_fail_verify_invalid_token(uc_exec, client, json_ver_req, uc_ver_req):
    '''Should return InvalidTokenError'''
    # Setup usecase mock
    uc_exec.side_effect = uc_ver.InvalidTokenError

    # Send test request
    response = client.post("/auth/register/verify/", json=json_ver_req)

    # Assert results
    uc_exec.assert_called_with(uc_ver_req)
    assert response.url == 'http://testserver/auth/register/verify/'
    assert 'invalid' in response.json().get('msg').lower()
    assert response.status_code == 400
