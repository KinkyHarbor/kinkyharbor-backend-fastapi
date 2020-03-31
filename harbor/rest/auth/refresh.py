'''This module contains all token refresh related routes'''

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from harbor.domain.common import message_responses
from harbor.domain.token import AccessRefreshTokens
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import token_refresh as uc_token_refresh


router = APIRouter()


class RefreshTokenForm(BaseModel):
    '''Form to request a refresh of the access and refresh token'''
    refresh_token: str


@router.post('/refresh/',
             summary='Refresh tokens (custom implementation)',
             response_model=AccessRefreshTokens,
             responses=message_responses({
                 400: 'Invalid token (Code: invalid_token)',
             }))
async def refresh(form: RefreshTokenForm, repos: RepoDict = Depends(get_repos)):
    '''Trades a refresh token for a new access and refresh token (custom implementation)'''
    uc = uc_token_refresh.TokenRefreshUseCase(rt_repo=repos['refresh_token'])
    uc_req = uc_token_refresh.TokenRefreshRequest(
        refresh_token=form.refresh_token
    )

    try:
        tokens = await uc.execute(uc_req)
        return tokens

    except uc_token_refresh.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                'code': 'invalid_token',
                'msg': 'Invalid token',
            }
        )
