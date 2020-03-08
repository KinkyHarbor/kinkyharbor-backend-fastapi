'''This module handles all routes for search operations'''

import logging

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from core.auth import validate_access_token
from core.db import get_db
from crud import users
from models.token import AccessTokenData


router = APIRouter()


@router.get('/', summary='Search for people, pages, groups and events')
async def search(q: str,
                 cat: str = 'all',
                 token_data: AccessTokenData = Depends(validate_access_token),
                 db: MotorDB = Depends(get_db)):
    '''Search for people, pages, groups and events'''
    all_cat = cat == 'all'
    cats = cat.split(',')

    if all_cat or 'user' in cats:
        user_list = await users.search(db, token_data.user_id, q)
    else:
        user_list = []

    return {
        'users': user_list
    }
