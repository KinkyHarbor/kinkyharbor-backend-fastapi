'''This module handles all routes for user operations'''

from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from harbor.core.auth import validate_access_token
from harbor.domain.common import Message
from harbor.domain.token import AccessTokenData
from harbor.domain.user import User
from harbor.repository.base import RepoDict, get_repos
from harbor.repository.mongo.common import get_db
from harbor.use_cases.user import (
    profile_get as uc_get_profile,
    profile_update as uc_update_profile,
)

router = APIRouter()


@router.get('/me/',
            summary='Get own user data',
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


@router.patch('/me/', summary='Set own user data', response_model=User)
async def set_user_me(user_info: uc_update_profile.UpdateUser,
                      token_data: AccessTokenData = Depends(
                          validate_access_token),
                      db: MotorDB = Depends(get_db)):
    '''Set your own user data.'''
    user = await users.set_info(db, token_data.user_id, user_info)
    return {'user': user.dict()}


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
