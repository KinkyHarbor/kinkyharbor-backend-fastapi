'''This module handles all routes for user operations'''

from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from harbor.core.auth import validate_access_token, get_current_active_user
from harbor.domain.common import Message
from harbor.domain.token import AccessTokenData
from harbor.domain.user import User, STRANGER_FIELDS, FRIEND_FIELDS
from harbor.repository.mongo import users
from harbor.repository.mongo.common import get_db
from harbor.use_cases.user.update_profile import UpdateUser

router = APIRouter()


@router.get('/me/', summary='Get own user data', response_model=User, response_model_by_alias=True)
async def get_user_me(current_user: User = Depends(get_current_active_user)):
    '''Get your own user data.'''
    return current_user.dict()


@router.patch('/me/', summary='Set own user data', response_model=User)
async def set_user_me(user_info: UpdateUser,
                      token_data: AccessTokenData = Depends(
                          validate_access_token),
                      db: MotorDB = Depends(get_db)):
    '''Set your own user data.'''
    user = await users.set_info(db, token_data.user_id, user_info)
    return {'user': user.dict()}


@router.get(
    '/{username}/',
    summary='Get user profile of a single user',
    response_model=User,
    responses={404: {"model": Message}}
)
async def get_user(username: str,
                   token_data: AccessTokenData = Depends(
                       validate_access_token),
                   db: MotorDB = Depends(get_db)):
    '''Get a user profile'''
    user = await users.get_by_username(db, username)
    if not user:
        return JSONResponse(
            status_code=404,
            content='User not found',
        )

    is_friend = token_data.user_id in user.friends
    include_fields = FRIEND_FIELDS if is_friend else STRANGER_FIELDS

    return {
        'isFriend': is_friend,
        'user': user.dict(include=include_fields),
    }
