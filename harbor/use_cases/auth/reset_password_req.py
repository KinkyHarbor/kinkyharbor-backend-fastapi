'''User requests a password reset'''

from pydantic import BaseModel, EmailStr

from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.helpers import email, debug
from harbor.repository.base import UserRepo, VerifTokenRepo
from harbor.worker.app import queue_task


class RequestPasswordResetRequest(BaseModel):
    '''Request for request password reset usecase'''
    email: EmailStr


class RequestPasswordResetUseCase:
    '''User requests a password reset'''

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo):
        self.user_repo = user_repo
        self.vt_repo = vt_repo

    async def execute(self, req: RequestPasswordResetRequest):
        '''Checks if user exists and sends a verification token'''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Fetch user by email
        user = await self.user_repo.get_by_login(req.email)
        if user:
            # User found => Send verification token
            token = await self.vt_repo.create_verif_token(user.id, VerifPur.RESET_PASSWORD)
            msg = email.prepare_reset_password(
                user.display_name,
                user.email,
                token.user_id,
                token.secret
            )
            queue_task('harbor.worker.tasks.email.send_mail', [msg.dict()])
