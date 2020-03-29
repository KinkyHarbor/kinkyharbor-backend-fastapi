'''This module handles all routes for user operations'''

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from harbor.core.auth import validate_access_token
from harbor.domain.common import Message
from harbor.domain.token import AccessTokenData
from harbor.domain.user import User
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.user import (
    profile_get as uc_get_profile,
    profile_update as uc_update_profile,
)

router = APIRouter()


@router.get('/me/',
            summary='Get own profile',
            response_model=uc_get_profile.GetProfileResponse,
            response_model_by_alias=True)
async def get_user_me(token_data: AccessTokenData = Depends(validate_access_token),
                      repos: RepoDict = Depends(get_repos)):
    '''Get your own user data.'''
    uc = uc_get_profile.GetProfileUsercase(user_repo=repos['user'])
    uc_req = uc_get_profile.GetProfileByIDRequest(
        requester=token_data.user_id,
        user_id=token_data.user_id,
    )
    return await uc.execute(uc_req)


class UpdateProfileForm(BaseModel):
    '''Form to update user profile'''
    bio: str = None
    gender: str = None


@router.patch('/me/', summary='Update own profile', response_model=User)
async def set_user_me(form: UpdateProfileForm,
                      token_data: AccessTokenData = Depends(
                          validate_access_token),
                      repos: RepoDict = Depends(get_repos)):
    '''Set your own user data.'''
    uc = uc_update_profile.UpdateProfileUsercase(user_repo=repos['user'])
    uc_req = uc_update_profile.UpdateProfileRequest(
        user_id=token_data.user_id,
        **form.dict(),
    )
    return await uc.execute(uc_req)


@router.get(
    '/{username}/',
    summary='Get user profile of a single user',
    response_model=uc_get_profile.GetProfileResponse,
    responses={404: {"model": Message}}
)
async def get_user(username: str,
                   token_data: AccessTokenData = Depends(
                       validate_access_token),
                   repos: RepoDict = Depends(get_repos)):
    '''Get a user profile'''
    uc = uc_get_profile.GetProfileUsercase(user_repo=repos['user'])
    uc_req = uc_get_profile.GetProfileByUsernameRequest(
        requester=token_data.user_id,
        username=username,
    )

    try:
        return await uc.execute(uc_req)
    except uc_get_profile.UserNotFoundError:
        return JSONResponse(
            status_code=404,
            content='User not found',
        )
