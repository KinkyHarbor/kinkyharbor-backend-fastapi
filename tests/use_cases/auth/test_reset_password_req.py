'''Unit tests for Request Password Reset usecase'''
# pylint: disable=too-many-arguments

from unittest import mock

import pytest

from harbor.domain.email import EmailMsg
from harbor.domain.token import VerificationToken, VerificationPurposeEnum as VerifPur
from harbor.domain.user import User
from harbor.repository.base import UserRepo, VerifTokenRepo
from harbor.use_cases.auth import reset_password_req as uc_pw_req


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a password reset request'''
    return uc_pw_req.RequestPasswordResetRequest(email='user@kh.test')


@pytest.fixture(name='user')
def fixture_user():
    '''Returns a user'''
    return User(
        id='507f1f77bcf86cd799439011',
        display_name='TestUser',
        email='user@kh.test',
    )


@pytest.fixture(name='verif_token')
def fixture_verif_token():
    '''Returns a verification_token'''
    return VerificationToken(
        user_id='507f1f77bcf86cd799439011',
        secret='test-secret',
        purpose=VerifPur.RESET_PASSWORD,
    )


@pytest.fixture(name='msg')
def fixture_msg():
    '''Returns an EmailMsg model'''
    return EmailMsg(
        to_name='test-User',
        to_email='user@kh.test',
        subject='test-subject',
        text='test-text-content',
        html='test-html-content',
    )


@pytest.mark.asyncio
@mock.patch('harbor.use_cases.auth.reset_password_req.queue_task')
@mock.patch('harbor.use_cases.auth.reset_password_req.email')
async def test_success(email, queue_task, uc_req, user, verif_token, msg):
    '''Should send a password reset link'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = user
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.create_verif_token.return_value = verif_token
    email.prepare_reset_password.return_value = msg

    # Call usecase
    uc = uc_pw_req.RequestPasswordResetUseCase(user_repo, vt_repo)
    await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('user@kh.test')
    vt_repo.create_verif_token.assert_called_with(
        '507f1f77bcf86cd799439011',
        VerifPur.RESET_PASSWORD,
    )
    email.prepare_reset_password.assert_called_with(
        'TestUser',
        'user@kh.test',
        '507f1f77bcf86cd799439011',
        'test-secret',
    )
    queue_task.assert_called_with(
        'harbor.worker.tasks.email.send_mail',
        [msg.dict()],
    )


@pytest.mark.asyncio
@mock.patch('harbor.use_cases.auth.reset_password_req.queue_task')
@mock.patch('harbor.use_cases.auth.reset_password_req.email')
async def test_fail(email, queue_task, uc_req):
    '''User not found => Don't send link'''
    # Create mocks
    user_repo = mock.Mock(UserRepo)
    user_repo.get_by_login.return_value = None
    vt_repo = mock.Mock(VerifTokenRepo)

    # Call usecase
    uc = uc_pw_req.RequestPasswordResetUseCase(user_repo, vt_repo)
    await uc.execute(uc_req)

    # Assert results
    user_repo.get_by_login.assert_called_with('user@kh.test')
    vt_repo.create_verif_token.assert_not_called()
    email.prepare_reset_password.assert_not_called()
    queue_task.assert_not_called()
