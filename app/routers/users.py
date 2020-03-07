'''This module handles all routes for user operations'''

from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from core.auth import validate_access_token, get_current_active_user
from core.db import get_db
from crud import users
from models.common import Message
from models.token import AccessTokenData
from models.user import UserDB, UpdateUser, STRANGER_FIELDS, FRIEND_FIELDS

router = APIRouter()


@router.get('/me/', summary='Get own user data')
async def get_user_me(current_user: UserDB = Depends(get_current_active_user)):
    '''Get your own user data.'''
    return {'user': current_user}


@router.post('/me/', summary='Set own user data')
async def set_user_me(user_info: UpdateUser,
                      token_data: AccessTokenData = Depends(
                          validate_access_token),
                      db: MotorDB = Depends(get_db)):
    '''Set your own user data.'''
    user = await users.set_info(db, token_data.user_id, user_info)
    return {'user': user}


@router.get(
    '/{user_id}/',
    summary='Get user profile of a single user',
    responses={404: {"model": Message}}
)
async def get_user(user_id: str,
                   token_data: AccessTokenData = Depends(
                       validate_access_token),
                   db: MotorDB = Depends(get_db)):
    '''Get a user profile'''
    user = await users.get(db, user_id)
    if not user:
        JSONResponse(
            status_code=404,
            content='User not found',
        )

    is_friend = token_data.user_id in user.friends
    include_fields = FRIEND_FIELDS if is_friend else STRANGER_FIELDS

    return {
        'isFriend': is_friend,
        'user': user.dict(include=include_fields),
    }
