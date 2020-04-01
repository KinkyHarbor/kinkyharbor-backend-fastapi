'''This module contains CRUD operations for users'''

import logging
from datetime import datetime
from typing import List, Dict

from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pydantic import parse_obj_as

from harbor.domain.user import BaseUser, User, UserWithPassword, UserFlags
from harbor.repository.base import UserRepo, UsernameTakenError
from harbor.repository.mongo.common import create_db_client


class UserMongoRepo(UserRepo):
    '''Repository for users in Mongo'''

    COLLECTION = 'users'

    def __init__(self):
        client = create_db_client()
        self.col = client[self.COLLECTION]

    async def ensure_indexes(self):
        '''Creates required indexes'''
        await self.col.create_index('username', unique=True)
        await self.col.create_index('email', unique=True)

    async def get(self, user_id: str) -> User:
        user_dict = await self.col.find_one(ObjectId(user_id))
        if user_dict:
            return User(**user_dict)

    async def get_by_login(self, login: str) -> UserWithPassword:
        user_dict = await self.col.find_one({'$or': [{'username': login}, {'email': login}]})
        if user_dict:
            return UserWithPassword(**user_dict)

    async def get_by_username(self, username: str) -> User:
        user_dict = await self.col.find_one({'username': username})
        if user_dict:
            return User(**user_dict)

    async def get_search(self, user_id: str,
                         search_string: str,
                         limit: int = 10) -> List[BaseUser]:
        cursor = self.col.find(
            filter={
                'username': {'$regex': search_string.lower()},
                '_id': {'$not': {'$eq': ObjectId(user_id)}},
                'is_verified': True,
            },
            projection={'display_name', 'username'},
            limit=limit,
        )

        user_list = await cursor.to_list(None)
        return parse_obj_as(List[BaseUser], user_list)

    async def add(self,
                  *,  # Force key words only
                  display_name: str,
                  email: str,
                  password_hash: str) -> User:
        # Create new user
        user = UserWithPassword(display_name=display_name,
                                email=email,
                                password_hash=password_hash)

        # Try to insert new user into database
        try:
            await self.col.insert_one(user.dict())
        except DuplicateKeyError as dup_error:
            if 'username' in str(dup_error):
                raise UsernameTakenError()
            return None

        # pylint: disable=no-member
        logging.info('%s: New user "%s" created', __name__, user.display_name)
        return User(**user.dict())

    async def set_password(self, user_id: str, password_hash: str) -> User:
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': password_hash}},
        )
        return User(**user_dict)

    async def set_flag(self, user_id: str, flag: UserFlags, value: bool) -> User:
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {flag.value: value}},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)

    async def set_info(self, user_id: str, user_info: Dict) -> User:
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': user_info},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)

    async def update_last_login(self, user_id: str):
        return await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )


async def create_repo() -> UserMongoRepo:
    '''Returns a new instance of the repo'''
    repo = UserMongoRepo()
    await repo.ensure_indexes()
    return repo
