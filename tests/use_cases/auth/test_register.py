'''Unit tests for Register User usecase'''
# pylint: disable=too-many-arguments

from unittest import mock

import pytest

from harbor.domain.email import EmailMsg
from harbor.domain.token import VerificationToken, VerificationPurposeEnum as VerifPur
from harbor.domain.user import User
from harbor.helpers import const
from harbor.repository.base import UserRepo, UsernameTakenError, EmailTakenError, VerifTokenRepo
from harbor.use_cases.auth import register as uc_reg


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a register request'''
    return uc_reg.RegisterRequest(
        display_name='TestUser',
        email='User@KH.test',
        password='VeryStrongTestPassword',
        is_adult=True,
        accept_privacy_and_terms=True,
    )


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
        secret='test-secret',
        purpose=VerifPur.REGISTER,
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
@mock.patch('harbor.use_cases.auth.register.celery_app')
@mock.patch('harbor.use_cases.auth.register.email')
@mock.patch('harbor.helpers.auth.get_password_hash')
async def test_success_new_user(get_pw_hash, email, celery_app, uc_req, user, verif_token, msg):
    '''Should register a user'''
    # Create mocks
    get_pw_hash.return_value = "test-secure-hash"
    user_repo = mock.Mock(UserRepo)
    user_repo.add.return_value = user
    vt_repo = mock.Mock(VerifTokenRepo)
    vt_repo.create_verif_token.return_value = verif_token
    email.prepare_register_verification.return_value = msg

    # Call usecase
    uc = uc_reg.RegisterUseCase(user_repo, vt_repo)
    res = await uc.execute(uc_req)

    # Assert results
    assert res is True
    get_pw_hash.assert_called_with('VeryStrongTestPassword')
    user_repo.add.assert_called_with(
        display_name='TestUser',
        email='user@kh.test',
        password_hash='test-secure-hash'
    )
    vt_repo.create_verif_token.assert_called_with(
        '507f1f77bcf86cd799439011',
        VerifPur.REGISTER,
    )
    email.prepare_register_verification.assert_called_with(
        'TestUser',
        'user@kh.test',
        'test-secret',
    )
    celery_app.send_task.assert_called_with(
        'harbor.worker.tasks.email.send_mail',
        args=[msg.dict()],
    )


@pytest.mark.asyncio
@mock.patch('harbor.use_cases.auth.register.celery_app')
@mock.patch('harbor.use_cases.auth.register.email')
@mock.patch('harbor.helpers.auth.get_password_hash')
async def test_success_existing_user(get_pw_hash, email, celery_app, uc_req, msg):
    '''Should inform user for registering existing mail address'''
    # Create mocks
    get_pw_hash.return_value = "test-secure-hash"
    user_repo = mock.Mock(UserRepo)
    user_repo.add.side_effect = EmailTakenError
    vt_repo = mock.Mock(VerifTokenRepo)
    email.prepare_register_email_exist.return_value = msg

    # Call usecase
    uc = uc_reg.RegisterUseCase(user_repo, vt_repo)
    res = await uc.execute(uc_req)

    # Assert results
    assert res is True
    get_pw_hash.assert_called_with('VeryStrongTestPassword')
    user_repo.add.assert_called_with(
        display_name='TestUser',
        email='user@kh.test',
        password_hash='test-secure-hash'
    )
    vt_repo.create_verif_token.assert_not_called()
    email.prepare_register_email_exist.assert_called_with(
        'TestUser',
        'user@kh.test'
    )
    celery_app.send_task.assert_called_with(
        'harbor.worker.tasks.email.send_mail',
        args=[msg.dict()],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('username', const.RESERVED_USERNAMES)
async def test_fail_reserved_username(username):
    '''Should return UsernameReservedError'''
    # Create request
    uc_req = uc_reg.RegisterRequest(
        display_name=username,
        email='user@kh.test',
        password='VeryStrongTestPassword',
        is_adult=True,
        accept_privacy_and_terms=True,
    )

    # Call usecase
    uc = uc_reg.RegisterUseCase(None, None)
    with pytest.raises(uc_reg.UsernameReservedError):
        await uc.execute(uc_req)


@pytest.mark.asyncio
@mock.patch('harbor.helpers.auth.get_password_hash')
async def test_fail_username_taken(get_pw_hash, uc_req):
    '''Should return UsernameTakenError'''
    # Create mocks
    get_pw_hash.return_value = "test-secure-hash"
    user_repo = mock.Mock(UserRepo)
    user_repo.add.side_effect = UsernameTakenError  # Error from repo

    # Call usecase
    uc = uc_reg.RegisterUseCase(user_repo, None)
    with pytest.raises(uc_reg.UsernameTakenError):
        await uc.execute(uc_req)
