'''User wants to reset his password'''

import enum

from pydantic import BaseModel

from harbor.domain.common import ObjectIdStr, StrongPasswordStr
from harbor.domain.token import TokenVerifyRequest as VerifTokenReq
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.domain.user import UserFlags
from harbor.helpers import auth
from harbor.repository.base import UserRepo, VerifTokenRepo


class ExecPasswordResetRequest(BaseModel):
    '''Request for verify registration usecase'''
    user_id: ObjectIdStr
    token: str
    password: StrongPasswordStr


class ExecResetPasswordResponse(enum.Enum):
    '''Response for verify registration usecase'''
    UPDATED = 'passwordUpdated'
    UPDATED_AND_VERIFIED = 'passwordUpdatedAndAccountVerified'


class InvalidTokenError(Exception):
    '''Provided token is invalid'''


class ExecResetPasswordUseCase:
    '''User wants to reset his password'''

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo):
        self.user_repo = user_repo
        self.vt_repo = vt_repo

    async def execute(self, req: ExecPasswordResetRequest) -> ExecResetPasswordResponse:
        '''Exchanges token for right to set new password and sets VERIFIED flag on user account

        Raises:
            InvalidTokenError: Provided token is invalid
        '''
        token = VerifTokenReq(secret=req.token,
                              user_id=req.user_id,
                              purpose=VerifPur.RESET_PASSWORD)
        valid = await self.vt_repo.verify_verif_token(token)
        if not valid:
            raise InvalidTokenError

        # Set new password
        password_hash = auth.get_password_hash(req.password)
        user = await self.user_repo.set_password(valid.user_id, password_hash)

        # Mark account as verified
        if not user.is_verified:
            await self.user_repo.set_flag(valid.user_id, UserFlags.VERIFIED, True)
            return ExecResetPasswordResponse.UPDATED_AND_VERIFIED
        return ExecResetPasswordResponse.UPDATED
