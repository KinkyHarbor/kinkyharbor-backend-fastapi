'''This module contains CRUD operations for users'''
# pylint: disable=no-member

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pydantic import parse_obj_as

from harbor.domain.user import BaseUser, User, UserWithPassword, UserFlags, UserInfo
from harbor.repository.base import UserRepo, UsernameTakenError, EmailTakenError
from harbor.repository.mongo.common import MongoBaseRepo


class UserMongoRepo(MongoBaseRepo, UserRepo):
    '''Repository for users in Mongo'''

    COLLECTION = 'users'

    def __init__(self):
        super().__init__()
        self.col = self.db[self.COLLECTION]

    async def __aenter__(self):
        await self.ensure_indexes()
        return self

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

    async def count_active_users(self, from_=timedelta(days=-30), to=timedelta()):
        '''Returns active user count'''
        datetime_from = datetime.now(timezone.utc) + from_
        datetime_to = datetime.now(timezone.utc) + to
        return await self.col.count_documents({
            'last_login': {
                '$gte': datetime_from,
                '$lte': datetime_to,
            }
        })

    async def add(self,
                  *,  # Force keywords only
                  display_name: str,
                  email: str,
                  password_hash: str) -> User:
        # Create new user
        user = UserWithPassword(display_name=display_name,
                                email=email,
                                password_hash=password_hash)

        # Try to insert new user into database
        try:
            user_dict = user.dict(exclude_none=True)
            result = await self.col.insert_one(user_dict)
        except DuplicateKeyError as dup_error:
            if 'username' in str(dup_error):
                raise UsernameTakenError(user.display_name)
            if 'email' in str(dup_error):
                raise EmailTakenError(user.email)
            raise dup_error

        logging.info('%s: New user "%s" created', __name__, user.display_name)
        user.id = result.inserted_id
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
        assert user_dict is not None, f'User should aways exist. User "{user_id}" not found'
        return User(**user_dict)

    async def set_info(self, user_id: str, user_info: UserInfo) -> User:
        user_info_dict = user_info.dict(exclude_none=True)
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': user_info_dict},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)

    async def update_last_login(self, user_id: str):
        return await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.now(timezone.utc)}}
        )


async def create_repo() -> UserMongoRepo:
    '''Returns a new instance of the repo'''
    repo = UserMongoRepo()
    await repo.ensure_indexes()
    return repo
