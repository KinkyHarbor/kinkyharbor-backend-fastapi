'''This module contains CRUD operations for users'''

import logging
from datetime import datetime
from bson.objectid import ObjectId
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB
from pymongo import ReturnDocument, TEXT
from pydantic import parse_obj_as

from models.user import (
    User, RegisterUser, UserDBIn, UserDB,
    UserFlags, UpdateUser, SearchUser
)
from core import auth

TABLE_NAME = 'users'


async def ensure_indexes(db: MotorDB):
    '''Creates required indexes.'''
    await db[TABLE_NAME].create_index('username', unique=True)
    await db[TABLE_NAME].create_index('email', unique=True)


async def get(db: MotorDB, user_id: str) -> User:
    '''Return single user by ID.'''
    user_dict = await db[TABLE_NAME].find_one(ObjectId(user_id))
    if user_dict:
        return User(**user_dict)


async def get_login(db: MotorDB, username: str, email: str = None) -> UserDB:
    '''Get single user by username or email.'''
    if not email:
        email = username

    user_dict = await db[TABLE_NAME].find_one({'$or': [{'username': username}, {'email': email}]})
    if user_dict:
        return UserDB(**user_dict)


async def search(db: MotorDB, user_id: str, search_string: str, limit: int = 10):
    '''Search users based on username'''
    cursor = db[TABLE_NAME].find(
        filter={'username': {'$regex': search_string.lower()}},
        projection={'display_name', 'username'},
        limit=limit,
    )

    user_list = await cursor.to_list(None)
    return parse_obj_as(List[SearchUser], user_list)


async def update_last_login(db: MotorDB, user_id: str):
    '''Updates last login timestamp for user'''
    return await db[TABLE_NAME].find_one_and_update(
        {'_id': ObjectId(user_id)}, {'$set': {'last_login': datetime.utcnow()}}
    )


async def register(db: MotorDB,
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
    result = await db[TABLE_NAME].insert_one(user.dict())
    logging.info('%s: New user "%s" created', __name__, user.display_name)
    return User(id=result.inserted_id, **user.dict())


async def set_password(db: MotorDB, user_id: str, password: str) -> User:
    '''Sets a new password for the user

    Returns
        User: Updated user
    '''
    hpass = auth.get_password_hash(password)
    user_dict = await db[TABLE_NAME].find_one_and_update(
        {'_id': ObjectId(user_id)},
        {'$set': {'hashed_password': hpass}},
        return_document=ReturnDocument.AFTER,
    )
    return User(**user_dict)


async def set_flag(db: MotorDB, user_id: str, flag: UserFlags, value: bool) -> User:
    '''Sets a flag on the user to True or False

    Returns
        User: Updated user
    '''
    if not isinstance(flag, UserFlags):
        raise ValueError(f'"{str(flag)}" is not a valid user flag')
    user_dict = await db[TABLE_NAME].find_one_and_update(
        {'_id': ObjectId(user_id)},
        {'$set': {flag.value: value}},
        return_document=ReturnDocument.AFTER,
    )
    return User(**user_dict)


async def set_info(db: MotorDB, user_id: str, user_info: UpdateUser) -> User:
    '''Sets info which allows direct update

    Returns
        User: Updated user
    '''
    user_dict = await db[TABLE_NAME].find_one_and_update(
        {'_id': ObjectId(user_id)},
        {'$set': user_info.dict()},
        return_document=ReturnDocument.AFTER,
    )
    return User(**user_dict)
