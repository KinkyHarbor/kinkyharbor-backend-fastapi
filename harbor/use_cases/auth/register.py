'''User registers a new account'''

from pydantic import BaseModel, EmailStr

from harbor.domain.common import StrictBoolTrue, DisplayNameStr, StrongPasswordStr
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.helpers import auth, debug, email, const
from harbor.repository import base as repo_base
from harbor.repository.base import UserRepo, VerifTokenRepo
from harbor.worker.app import queue_task


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

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo):
        self.user_repo = user_repo
        self.vt_repo = vt_repo

    async def execute(self, req: RegisterRequest) -> bool:
        '''Validate info and add new user. Sends verification mail on success.

        Raises:
            UsernameReservedError: Username is a reserved name. E.g. "admin"
            UsernameTakenError: Username is already taken
        '''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict(exclude={"password"}))

        # Force email to lowercase
        req.email = req.email.lower()

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

        except repo_base.EmailTakenError:
            # Prepare password reset mail
            msg = email.prepare_register_email_exist(
                req.display_name,
                req.email,
            )

        else:
            # Prepare verification mail
            token = await self.vt_repo.create_verif_token(user.id, VerifPur.REGISTER)
            msg = email.prepare_register_verification(
                req.display_name,
                req.email,
                token.secret
            )

        # Send mail and confirm success
        queue_task('harbor.worker.tasks.email.send_mail', [msg.dict()])

        # Return success
        return True
