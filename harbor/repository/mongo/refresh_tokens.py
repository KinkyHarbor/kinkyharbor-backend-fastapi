'''This module contains CRUD operations for refresh tokens'''

from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB

from harbor.domain.common import ObjectIdStr
from harbor.domain.token import RefreshToken

TABLE_NAME = 'refresh_tokens'


async def ensure_indexes(db: MotorDB):
    '''Creates required indexes.'''
    # Drop refresh token after 3 days of inactivity
    await db[TABLE_NAME].create_index('created_on', expireAfterSeconds=3*60*60*24)


async def create_token(db: MotorDB, user_id: ObjectIdStr):
    '''Creates and returns a verification token'''
    token = RefreshToken(user_id=user_id)
    await db[TABLE_NAME].insert_one(token.dict())
    return token


async def replace_token(db: MotorDB, token: RefreshToken):
    '''Replaces a refresh token

    Returns
        RefreshToken: Token is valid, new token is returned
        None: Token is invalid
    '''
    db_token_dict = await db[TABLE_NAME].find_one_and_delete({
        'secret': token.secret,
        'user_id': token.user_id
    })

    if db_token_dict:
        # Valid token found, create new token
        return await create_token(db, token.user_id)
