'''User registers a new account'''

from pydantic import BaseModel, EmailStr, validator, Field

from harbor.core import auth, email, settings
from harbor.domain.common import DisplayNameStr, StrongPasswordStr
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.repository import base as repo_base
from harbor.repository.base import UserRepo, VerifTokenRepo

class RegisterRequest(BaseModel):
    '''Required form data for registering a user'''
    username: DisplayNameStr
    email: EmailStr
    password: StrongPasswordStr = Field(...,
                                        description='Password should either be 16 characters or '
                                        'longer (passphrase). Or should be minimum 8 long and '
                                        'have lower case, upper case and a digit.')
    isAdult: bool = Field(...,
                          title='Is adult',
                          description='Confirms the user is an adult')
    acceptPrivacyAndTerms: bool

    @validator('isAdult')
    @classmethod
    def must_be_adult(cls, is_adult):
        '''User must be an adult'''
        if not is_adult:
            raise ValueError('User must be an adult')
        return True

    @validator('acceptPrivacyAndTerms')
    @classmethod
    def must_accept_priv_and_terms(cls, accepted):
        '''User must accept Privacy policy and Terms and conditions'''
        if not accepted:
            raise ValueError(
                'User must accept Privacy policy and Terms and conditions to use this platform')
        return True


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
        username = req.username.lower()
        if username in settings.RESERVED_USERNAMES:
            raise UsernameReservedError()

        # Create a new user in the database
        try:
            user = await self.user_repo.add(
                display_name=req.username,
                email=req.email,
                password_hash=auth.get_password_hash(req.password)
            )
        except repo_base.UsernameTakenError:
            # Translate error
            raise UsernameTakenError

        # Send mail to user
        recipient = email.get_address(req.username, req.email)
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
