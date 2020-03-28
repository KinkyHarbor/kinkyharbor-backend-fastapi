'''This module contains all token refresh related routes'''

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from harbor.domain.common import Message
from harbor.domain.token import AccessRefreshTokens
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import token_refresh as uc_token_refresh


router = APIRouter()


class ReplaceRefreshToken(BaseModel):
    '''Request to replace a refresh and access token'''
    refresh_token: str


@router.post('/refresh/', response_model=AccessRefreshTokens, responses={401: {"model": Message}})
async def refresh(req: ReplaceRefreshToken, repos: RepoDict = Depends(get_repos)):
    '''Trades a refresh token to a new access and refresh token (custom implementation)'''
    uc = uc_token_refresh.TokenRefreshUseCase(rt_repo=repos['refresh_token'])
    uc_req = uc_token_refresh.TokenRefreshRequest(
        refresh_token=req.refresh_token
    )

    try:
        tokens = await uc.execute(uc_req)
        return tokens

    except uc_token_refresh.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={'msg': 'Invalid refresh token'}
        )
