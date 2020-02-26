import logging
from starlette.testclient import TestClient

from main import app

client = TestClient(app)


def test_redirect_root_to_docs():
    response = client.get("/")
    logging.warning(response.url)
    assert response.status_code == 200
    assert response.url == 'http://testserver/docs'
