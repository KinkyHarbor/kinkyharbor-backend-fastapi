'''This module handles all routes for user operations'''

from fastapi import APIRouter, Depends

from models.user import UserDB
from core.auth import get_current_active_user

router = APIRouter()


@router.get('/me', summary='Get own user data')
async def read_users_me(current_user: UserDB = Depends(get_current_active_user)):
    '''Get your own user data.'''
    return current_user
