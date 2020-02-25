from bson.objectid import ObjectId

from db.mongo import db
from models.user import User, RegisterUser, UserDBIn, UserDBOut
from core import auth


async def get(id: str):
    user_dict = await db.users.find_one({'_id': ObjectId(id)})
    return User(**user_dict)


async def get_login(username: str):
    user_dict = await db.users.find_one({'$or': [{'username': username}, {'email': username}]})
    return UserDBOut(**user_dict)


async def register(reg_user: RegisterUser, is_admin: bool = False):
    hpass = auth.get_password_hash(reg_user.password)
    user = UserDBIn(**reg_user.dict(),
                    hashed_password=hpass, is_admin=is_admin)
    return await db.users.insert_one(user.dict())
