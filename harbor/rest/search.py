'''This module handles all routes for search operations'''

from typing import List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB
from pydantic import BaseModel

from harbor.core.auth import validate_access_token
from harbor.domain.token import AccessTokenData
from harbor.domain.user import BaseUser
from harbor.repository.mongo import users
from harbor.repository.mongo.common import get_db


router = APIRouter()


class SearchResult(BaseModel):
    '''Result model for generic search'''
    users: List[BaseUser] = []
    groups: List = []
    pages: List = []
    events: List = []


@router.get('/', summary='Search for people, pages, groups and events', response_model=SearchResult)
async def search(q: str,
                 cat: str = 'all',
                 token_data: AccessTokenData = Depends(validate_access_token),
                 repos: MotorDB = Depends(get_db)):
    '''Search for people, pages, groups and events'''
    all_cat = cat == 'all'
    cats = cat.split(',')

    if all_cat or 'user' in cats:
        user_list = await users.get_search(db, token_data.user_id, q)
    else:
        user_list = []

    return SearchResult(users=user_list)
