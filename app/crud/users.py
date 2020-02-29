from bson.objectid import ObjectId
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from db.mongo import get_db
from models.user import User, RegisterUser, UserDBIn, UserDBOut
from core import auth


async def get(db: MotorDB, user_id: str):
    '''Return single user by ID.'''
    user_dict = await db.users.find_one({'_id': ObjectId(user_id)})
    return User(**user_dict)


async def get_login(db: MotorDB, username: str, email: str = None):
    '''Return single user by username or email.'''
    if not email:
        email = username

    user_dict = await db.users.find_one({'$or': [{'username': username}, {'email': email}]})
    if user_dict:
        return UserDBOut(**user_dict)


async def register(db: MotorDB,
                   reg_user: RegisterUser,
                   is_admin: bool = False,
                   is_verified: bool = False):
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
    return await db.users.insert_one(user.dict())
