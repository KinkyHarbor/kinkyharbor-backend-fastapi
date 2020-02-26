from bson.objectid import ObjectId

from db.mongo import get_db
from models.user import User, RegisterUser, UserDBIn, UserDBOut
from core import auth


async def get(user_id: str):
    '''Return single user by ID.'''
    db = get_db()
    user_dict = await db.users.find_one({'_id': ObjectId(user_id)})
    return User(**user_dict)


async def get_login(username: str):
    '''Return single user by username or email.'''
    db = get_db()
    user_dict = await db.users.find_one({'$or': [{'username': username}, {'email': username}]})
    return UserDBOut(**user_dict)


async def register(reg_user: RegisterUser, is_admin: bool = False, is_verified: bool = False):
    '''Add a new user.'''
    db = get_db()
    hpass = auth.get_password_hash(reg_user.password)
    user = UserDBIn(**reg_user.dict(),
                    hashed_password=hpass,
                    is_admin=is_admin,
                    is_verified=is_verified)
    return await db.users.insert_one(user.dict())
