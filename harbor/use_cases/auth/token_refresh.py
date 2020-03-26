'''User trades refresh token for new access and refresh token'''

from pydantic import BaseModel, constr

from harbor.core import auth
from harbor.domain.token import AccessRefreshTokens, RefreshToken
from harbor.repository.base import RefreshTokenRepo


class TokenRefreshRequest(BaseModel):
    '''Request for verify registration usecase'''
    refresh_token: constr(min_length=1)


class InvalidTokenError(Exception):
    '''Provided token is invalid'''


class TokenRefreshUseCase:
    '''User trades refresh token for new access and refresh token'''

    def __init__(self, rt_repo: RefreshTokenRepo):
        self.rt_repo = rt_repo

    async def execute(self, req: TokenRefreshRequest) -> AccessRefreshTokens:
        '''Exchanges refresh token to new access and refresh token

        Raises:
            InvalidTokenError: Provided token is invalid
        '''
        (user_id, token) = req.refresh_token.split(':')
        old_ref_token = RefreshToken(secret=token, user_id=user_id)
        new_ref_token = await self.rt_repo.replace_token(old_ref_token)

        if new_ref_token:
            # Token is valid => Generate new tokens
            access_token = await auth.create_access_token(data={"sub": f'user:{user_id}'})
            return AccessRefreshTokens(
                access_token=access_token,
                refresh_token=f'{user_id}:{new_ref_token.secret}',
            )

        # Token is invalid => No new refresh token was generated
        raise InvalidTokenError()
