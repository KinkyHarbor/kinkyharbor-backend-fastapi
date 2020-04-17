'''User registers a new account'''

from pydantic import BaseModel, EmailStr

from harbor.domain.common import StrictBoolTrue, DisplayNameStr, StrongPasswordStr
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.helpers import auth, email, const
from harbor.repository import base as repo_base
from harbor.repository.base import UserRepo, VerifTokenRepo


class RegisterRequest(BaseModel):
    '''Request to register a user'''
    display_name: DisplayNameStr
    email: EmailStr
    password: StrongPasswordStr
    is_adult: StrictBoolTrue
    accept_privacy_and_terms: StrictBoolTrue


class UsernameReservedError(Exception):
    '''Username is a reserved username'''


class UsernameTakenError(Exception):
    '''Username is already taken'''


class RegisterUseCase:
    '''User registers a new account'''

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo, background_tasks):
        self.user_repo = user_repo
        self.vt_repo = vt_repo
        self.bg_tasks = background_tasks  # TODO: Move to tool like Celery

    async def execute(self, req: RegisterRequest) -> bool:
        '''Validate info and add new user. Sends verification mail on success.

        Raises:
            UsernameReservedError: Username is a reserved name. E.g. "admin"
            UsernameTakenError: Username is already taken
        '''

        # Check if username is reserved
        username = req.display_name.lower()
        if username in const.RESERVED_USERNAMES:
            raise UsernameReservedError()

        # Create a new user in the database
        try:
            user = await self.user_repo.add(
                display_name=req.display_name,
                email=req.email,
                password_hash=auth.get_password_hash(req.password)
            )
        except repo_base.UsernameTakenError:
            # Translate error
            raise UsernameTakenError

        # Send mail to user
        recipient = email.get_address(req.display_name, req.email)
        if user:
            # Get verification token
            token = await self.vt_repo.create_verif_token(user.id, VerifPur.REGISTER)

            # Send verification mail
            msg = email.prepare_register_verification(recipient, token.secret)
        else:
            # Send password reset mail
            msg = email.prepare_register_email_exist(recipient)

        # Send mail and confirm success
        self.bg_tasks.add_task(email.send_mail, msg)
        return True
