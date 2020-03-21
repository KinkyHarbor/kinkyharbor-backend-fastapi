'''This module contains CRUD operations for users'''

import logging
from datetime import datetime
from typing import List

from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pydantic import parse_obj_as

from harbor.domain.user import (
    User, RegisterUser, UserDBIn, UserDB,
    UserFlags, UpdateUser, SearchUser
)
from harbor.core import auth
from harbor.repository.mongo.common import create_db_client


class UserMongoRepo:
    '''Repository for Users in Mongo'''

    COLLECTION = 'users'

    def __init__(self):
        client = create_db_client()
        self.col = client[self.COLLECTION]

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index('username', unique=True)
        await self.col.create_index('email', unique=True)

    async def get(self, user_id: str) -> User:
        '''Return single user by ID.'''
        user_dict = await self.col.find_one(ObjectId(user_id))
        if user_dict:
            return User(**user_dict)

    async def get_login(self, username: str, email: str = None) -> UserDB:
        '''Get single user by username or email.'''
        if not email:
            email = username

        user_dict = await self.col.find_one({'$or': [{'username': username}, {'email': email}]})
        if user_dict:
            return UserDB(**user_dict)

    async def get_by_username(self, username: str) -> User:
        '''Get single user by username.'''
        user_dict = await self.col.find_one({'username': username})
        if user_dict:
            return User(**user_dict)

    async def search(self, user_id: str,
                     search_string: str, limit: int = 10) -> List[SearchUser]:
        '''Search users based on username'''
        cursor = self.col.find(
            filter={'username': {'$regex': search_string.lower()},
                    '_id': {'$not': {'$eq': ObjectId(user_id)}}},
            projection={'display_name', 'username'},
            limit=limit,
        )

        user_list = await cursor.to_list(None)
        return parse_obj_as(List[SearchUser], user_list)

    async def update_last_login(self, user_id: str):
        '''Updates last login timestamp for user'''
        return await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)}, {
                '$set': {'last_login': datetime.utcnow()}}
        )

    async def register(self,
                       reg_user: RegisterUser) -> User:
        '''Add a new user.

        Raises:
            DuplicateKeyError: Either username or email is already in use
        '''
        # Create new user
        hpass = auth.get_password_hash(reg_user.password)
        user = UserDBIn(display_name=reg_user.username,
                        email=reg_user.email,
                        hashed_password=hpass)
        result = await self.col.insert_one(user.dict())
        logging.info('%s: New user "%s" created', __name__, user.display_name)
        return User(id=result.inserted_id, **user.dict())

    async def set_password(self, user_id: str, password: str) -> User:
        '''Sets a new password for the user

        Returns
            User: Updated user
        '''
        hpass = auth.get_password_hash(password)
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {'hashed_password': hpass}},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)

    async def set_flag(self, user_id: str, flag: UserFlags, value: bool) -> User:
        '''Sets a flag on the user to True or False

        Returns
            User: Updated user
        '''
        if not isinstance(flag, UserFlags):
            raise ValueError(f'"{str(flag)}" is not a valid user flag')
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': {flag.value: value}},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)

    async def set_info(self, user_id: str, user_info: UpdateUser) -> User:
        '''Sets info which allows direct update

        Returns
            User: Updated user
        '''
        user_dict = await self.col.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': user_info.dict()},
            return_document=ReturnDocument.AFTER,
        )
        return User(**user_dict)


async def create_repo() -> UserMongoRepo:
    '''Returns a new instance of the repo'''
    repo = UserMongoRepo()
    await repo.ensure_indexes()
    return repo
