'''User wants to verify his registration'''

from pydantic import BaseModel, constr

from harbor.domain.token import TokenVerifyRequest as VerifTokenReq
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.domain.user import UserFlags
from harbor.helpers import debug
from harbor.repository.base import UserRepo, VerifTokenRepo


class RegisterVerifyRequest(BaseModel):
    '''Request for verify registration usecase'''
    secret: constr(min_length=1)


class InvalidTokenError(Exception):
    '''Provided token is invalid'''


class RegisterVerifyUseCase:
    '''User wants to verify his registration'''

    def __init__(self, user_repo: UserRepo, vt_repo: VerifTokenRepo):
        self.user_repo = user_repo
        self.vt_repo = vt_repo

    async def execute(self, req: RegisterVerifyRequest) -> bool:
        '''Verifies token and sets VERIFIED flag on user account

        Raises:
            InvalidTokenError: Provided token is invalid
        '''
        # Log call for debugging
        debug.log_call(__name__, "execute", req.dict())

        # Verify token
        token_req = VerifTokenReq(secret=req.secret,
                                  purpose=VerifPur.REGISTER)
        valid = await self.vt_repo.verify_verif_token(token_req)
        if not valid:
            raise InvalidTokenError()

        # Mark account as verified and confirm success
        await self.user_repo.set_flag(valid.user_id, UserFlags.VERIFIED, True)
        return True
