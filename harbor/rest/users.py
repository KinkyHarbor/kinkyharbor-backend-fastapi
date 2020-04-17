'''This module handles all routes for user operations'''

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from harbor.domain.common import message_responses
from harbor.domain.token import AccessTokenData
from harbor.domain.user import User, FRIEND_FIELDS, STRANGER_FIELDS
from harbor.repository.base import RepoDict, get_repos
from harbor.rest.auth.base import validate_access_token
from harbor.use_cases.user import (
    profile_get as uc_get_profile,
    profile_update as uc_update_profile,
)

router = APIRouter()


@router.get('/me/',
            summary='Get own profile',
            response_model=uc_get_profile.GetProfileResponse,
            response_model_by_alias=False)
async def get_user_me(token_data: AccessTokenData = Depends(validate_access_token),
                      repos: RepoDict = Depends(get_repos)):
    '''Get your own user data.'''
    uc = uc_get_profile.GetProfileUseCase(user_repo=repos['user'])
    uc_req = uc_get_profile.GetProfileByIDRequest(
        requester=token_data.user_id,
        user_id=token_data.user_id,
    )
    return await uc.execute(uc_req)


class UpdateProfileForm(BaseModel):
    '''Form to update user profile'''
    bio: str = None
    gender: str = None


@router.patch('/me/',
              summary='Update own profile',
              response_model=User,
              response_model_by_alias=False)
async def set_user_me(form: UpdateProfileForm,
                      token_data: AccessTokenData = Depends(
                          validate_access_token),
                      repos: RepoDict = Depends(get_repos)):
    '''Set your own user data.'''
    uc = uc_update_profile.UpdateProfileUseCase(user_repo=repos['user'])
    uc_req = uc_update_profile.UpdateProfileRequest(
        user_id=token_data.user_id,
        **form.dict(),
    )
    return await uc.execute(uc_req)


DESC_GET_USER_PROFILE = (
    "Get a user profile.<br/><br/>"
    "Note: The whole User object will always be returned. Depending if it's your own profile, "
    "it's a friend or you're no friends, the profile will be filled. Field \"exposed_fields\" "
    "will have a list of all filled fields. Fields which are not in this list will receive a "
    "default value.<br/><br/>"
    "Stranger fields: {}<br/>"
    "Friend fields: {}"
).format(", ".join(sorted(STRANGER_FIELDS)), ", ".join(sorted(FRIEND_FIELDS)))


@router.get(
    '/{username}/',
    summary='Get user profile of a single user',
    description=DESC_GET_USER_PROFILE,
    response_model=uc_get_profile.GetProfileResponse,
    response_model_by_alias=False,
    responses=message_responses({
        404: 'User not found (Code: not_found)',
    }))
async def get_user(username: str,
                   token_data: AccessTokenData = Depends(
                       validate_access_token),
                   repos: RepoDict = Depends(get_repos)):
    '''Get a user profile.'''
    uc = uc_get_profile.GetProfileUseCase(user_repo=repos['user'])
    uc_req = uc_get_profile.GetProfileByUsernameRequest(
        requester=token_data.user_id,
        username=username,
    )

    try:
        return await uc.execute(uc_req)
    except uc_get_profile.UserNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                'code': 'not_found',
                'msg': 'User not found',
            },
        )
