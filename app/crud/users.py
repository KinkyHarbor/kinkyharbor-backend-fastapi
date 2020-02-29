'''This module contains CRUD operations for users'''
from bson.objectid import ObjectId
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from models.user import User, RegisterUser, UserDBIn, UserDBOut, UserFlags
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


async def get_login(db: MotorDB, username: str, email: str = None) -> UserDBOut:
    '''Return single user by username or email.'''
    if not email:
        email = username

    user_dict = await db[TABLE_NAME].find_one({'$or': [{'username': username}, {'email': email}]})
    if user_dict:
        return UserDBOut(**user_dict)


async def register(db: MotorDB,
                   reg_user: RegisterUser,
                   is_admin: bool = False,
                   is_verified: bool = False) -> User:
    '''Add a new user.

    Raises:
        DuplicateKeyError: Either username or email is already in use
    '''
    # Create new user
    hpass = auth.get_password_hash(reg_user.password)
    user = UserDBIn(**reg_user.dict(),
                    hashed_password=hpass,
                    is_admin=is_admin,
                    is_verified=is_verified)
    result = await db[TABLE_NAME].insert_one(user.dict())
    return User(id=result.inserted_id, **user.dict())


async def set_flag(db: MotorDB, user_id: str, flag: UserFlags, value: bool):
    if not isinstance(flag, UserFlags):
        raise ValueError(f'"{str(flag)}" is not a valid user flag')
    return await db[TABLE_NAME].find_one_and_update({'_id': ObjectId(user_id)}, {'$set': {flag.value: value}})
