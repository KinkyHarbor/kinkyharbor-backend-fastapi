'''Unit tests for Execute Password Reset usecase'''
# pylint: disable=unused-argument,too-many-arguments

from unittest import mock

import pytest

from harbor.domain.token import (
    VerificationToken,
    TokenVerifyRequest as VerifReq,
    VerificationPurposeEnum as VerifPur,
)
from harbor.domain.user import User
from harbor.repository.base import UserRepo, VerifTokenRepo
from harbor.use_cases.auth import reset_password_exec as uc_exec


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a execute password reset request'''
    return uc_exec.ExecPasswordResetRequest(
        user_id='507f1f77bcf86cd799439111',
        token='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
        password='VeryStrongPassword',
    )


@pytest.fixture(name='verif_token_req')
def fixture_verif_token_req():
    '''Returns a verification token request'''
    return VerifReq(
        user_id='507f1f77bcf86cd799439111',
        secret='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
        purpose=VerifPur.RESET_PASSWORD,
    )


@pytest.fixture(name='verif_token')
def fixture_test_verif_token():
    '''Returns a verification token'''
    return VerificationToken(
        id='507f1f77bcf86cd799439000',
        secret='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
        purpose=VerifPur.RESET_PASSWORD,
        user_id='507f1f77bcf86cd799439111',
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('is_verified,expected', [
    (True, uc_exec.ExecResetPasswordResponse.UPDATED),
    (False, uc_exec.ExecResetPasswordResponse.UPDATED_AND_VERIFIED),
])
@mock.patch('harbor.core.auth.get_password_hash')
async def test_success(get_pw_hash, is_verified, expected, freezer, uc_req,
                       verif_token, verif_token_req):
    '''Should successfully verify a verification token'''
    # Create mocks
    get_pw_hash.return_value = "test-secure-hash"
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.verify_verif_token.return_value = verif_token
    user_repo = mock.Mock(UserRepo)
    user_repo.set_password.return_value = User(
        display_name='TestUser',
        is_verified=is_verified,
    )

    # Call usecase
    uc = uc_exec.ExecResetPasswordUseCase(user_repo, vt_repo)
    result = await uc.execute(uc_req)

    # Assert results
    vt_repo.verify_verif_token.assert_called_with(verif_token_req)
    user_repo.set_password.assert_called_with(
        '507f1f77bcf86cd799439111',
        "test-secure-hash",
    )
    assert result is expected


@pytest.mark.asyncio
async def test_fail_invalid_token(freezer, uc_req, verif_token_req):
    '''Should throw InvalidTokenError if token is not valid'''
    # Create mocks
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.verify_verif_token.return_value = None
    user_repo = mock.Mock(UserRepo)

    # Call usecase
    uc = uc_exec.ExecResetPasswordUseCase(user_repo, vt_repo)
    with pytest.raises(uc_exec.InvalidTokenError):
        await uc.execute(uc_req)

    # Assert results
    vt_repo.verify_verif_token.assert_called_with(verif_token_req)
    user_repo.assert_not_called()
