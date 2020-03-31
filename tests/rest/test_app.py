'''Test generic behavior of rest api'''

import logging

import pytest
from starlette.testclient import TestClient

from harbor.app import app


@pytest.fixture(name="client")
def fixture_client():
    '''Returns a test client'''
    return TestClient(app)


def test_redirect_root_to_docs(client):
    '''Accessing root should redirect you to the docs'''
    response = client.get("/")
    logging.warning(response.url)
    assert response.status_code == 200
    assert response.url == 'http://testserver/docs'
