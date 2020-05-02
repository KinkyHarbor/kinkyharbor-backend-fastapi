'''Unit tests for Settings helper'''

from harbor.helpers.settings import get_jwt_key, get_settings


def test_get_jwt_keys(monkeypatch, tmp_path):
    '''Should read and return an ECDSA key'''
    # Set JWT Key Path to temporary dir
    monkeypatch.setenv("JWT_KEY_PATH", tmp_path)
    get_settings.cache_clear()

    # Write test file
    key_file = tmp_path / "test-jwt-key.pem"
    key_file.write_text("test-ecdsa-key")

    # Read the JWT key
    get_jwt_key.cache_clear()
    result = get_jwt_key("test-jwt-key")

    # Assert result
    assert result == "test-ecdsa-key"
