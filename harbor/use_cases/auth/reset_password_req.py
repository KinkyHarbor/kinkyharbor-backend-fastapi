'''User requests a password reset'''

from pydantic import BaseModel, EmailStr

from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.helpers import email
from harbor.repository.base import UserRepo, VerifTokenRepo


class RequestPasswordResetRequest(BaseModel):
    '''Request for request password reset usecase'''
    email: EmailStr


class RequestPasswordResetUseCase:
    '''User requests a password reset'''

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo, background_tasks):
        self.user_repo = user_repo
        self.vt_repo = vt_repo
        self.bg_tasks = background_tasks  # TODO: Move to tool like Celery

    async def execute(self, req: RequestPasswordResetRequest):
        '''Checks if user exists and sends a verification token'''
        user = await self.user_repo.get_by_login(req.email)
        if user:
            # User found => Send verification token
            token = await self.vt_repo.create_verif_token(user.id, VerifPur.RESET_PASSWORD)
            recipient = email.get_address(user.display_name, user.email)
            msg = email.prepare_reset_password(
                recipient, token.user_id, token.secret)
            self.bg_tasks.add_task(email.send_mail, msg)
