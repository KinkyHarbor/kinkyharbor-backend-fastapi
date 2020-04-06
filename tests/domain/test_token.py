'''Unit tests for token domain'''

import pytest
from pydantic import ValidationError

from harbor.domain import token
from harbor.domain.token import VerificationPurposeEnum as VerifPur


# ================================
# =        SecretToken        =
# ================================

def test_success_secrettoken_secret_provided():
    '''Values should stay the same if provided'''
    sec_token = token.SecretToken(
        secret='test-secret',
    )
    assert sec_token.secret == 'test-secret'


def test_success_secrettoken_secret_empty():
    '''Should automatically generate random secret'''
    sec_token = token.SecretToken()
    for _ in range(10):
        sec_token2 = token.SecretToken()
        assert len(sec_token2.secret) > 0
        assert sec_token.secret != sec_token2.secret


# ================================
# =        VerifTokenData        =
# ================================

@pytest.mark.parametrize("purpose", [VerifPur.REGISTER])
def test_success_veriftokendata_user_id_not_required(purpose):
    '''User ID should not be required for following verification purposes'''
    token.VerifTokenData(secret='test-secret', purpose=purpose)


@pytest.mark.parametrize("purpose", [VerifPur.RESET_PASSWORD, VerifPur.CHANGE_EMAIL])
def test_fail_veriftokendata_user_id_required(purpose):
    '''User ID is required for following verification purposes'''
    with pytest.raises(ValidationError) as info:
        token.VerifTokenData(secret='test-secret', purpose=purpose)
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "mandatory" in err['msg'].lower()
