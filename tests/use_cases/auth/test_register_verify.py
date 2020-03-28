'''Unit tests for Verify Register User usecase'''
# pylint: disable=unused-argument

from unittest import mock

import pytest

from harbor.domain.token import (
    VerificationToken,
    VerificationTokenRequest as VerifReq,
    VerificationPurposeEnum as VerifPur,
)
from harbor.domain.user import User, UserFlags
from harbor.repository.base import UserRepo, VerifTokenRepo
from harbor.use_cases.auth import register_verify as uc_user_reg_ver


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a login request'''
    return uc_user_reg_ver.RegisterVerifyRequest(
        secret='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM'
    )


@pytest.fixture(name='verif_token_req')
def fixture_test_verif_token_req():
    '''Returns a verification token request'''
    return VerifReq(
        secret='-qEfNMazB8jg67-EMTZP_gKBok18952RCbrfhyCudOM',
        purpose=VerifPur.REGISTER,
    )


@pytest.fixture(name='verif_token')
def fixture_test_verif_token():
    '''Returns a verification token'''
    return VerificationToken(
        id='507f1f77bcf86cd799439000',
        purpose=VerifPur.REGISTER,
        user_id='507f1f77bcf86cd799439111',
    )


@pytest.mark.asyncio
async def test_success(freezer, uc_req, verif_token, verif_token_req):
    '''Should successfully verify a verification token'''
    # Create mocks
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.verify_verif_token.return_value = verif_token
    user_repo = mock.Mock(UserRepo)
    user_repo.set_flag.return_value = User(display_name='TestUser')

    # Call usecase
    uc = uc_user_reg_ver.RegisterVerifyUseCase(user_repo, vt_repo)
    success = await uc.execute(uc_req)

    # Assert results
    vt_repo.verify_verif_token.assert_called_with(verif_token_req)
    user_repo.set_flag.assert_called_with(
        '507f1f77bcf86cd799439111',
        UserFlags.VERIFIED,
        True
    )
    assert success is True


@pytest.mark.asyncio
async def test_fail_invalid_token(freezer, uc_req, verif_token_req):
    '''Should throw InvalidTokenError if token is not valid'''
    # Create mocks
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.verify_verif_token.return_value = None
    user_repo = mock.Mock(UserRepo)

    # Call usecase
    uc = uc_user_reg_ver.RegisterVerifyUseCase(user_repo, vt_repo)
    with pytest.raises(uc_user_reg_ver.InvalidTokenError):
        await uc.execute(uc_req)

    # Assert results
    vt_repo.verify_verif_token.assert_called_with(verif_token_req)
    user_repo.assert_not_called()
