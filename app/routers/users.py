'''This module handles all routes for user operations'''

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from models.user import UserDBOut
from core.auth import get_current_active_user
from core.db import get_db

router = APIRouter()


@router.get('/me', summary='Get own user data')
async def read_users_me(current_user: UserDBOut = Depends(get_current_active_user),
                        db: MotorDB = Depends(get_db)):
    '''Get your own user data.'''
    return current_user
