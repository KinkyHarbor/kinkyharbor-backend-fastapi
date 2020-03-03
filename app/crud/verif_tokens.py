'''This module contains CRUD operations for tokens'''

from motor.motor_asyncio import AsyncIOMotorDatabase as MotorDB
from pymongo import ReturnDocument

from models.common import ObjectIdStr
from models.token import VerificationToken, VerificationTokenRequest
from models.token import VerificationPurposeEnum as VerifPur

TABLE_NAME = 'verif_tokens'


async def ensure_indexes(db: MotorDB):
    '''Creates required indexes.'''
    await db[TABLE_NAME].create_index('secret', unique=True)
    await db[TABLE_NAME].create_index('created_on', expireAfterSeconds=3600)


async def create_verif_token(db: MotorDB, user_id: ObjectIdStr, purpose: VerifPur):
    '''Creates and returns a verification token'''
    token_req = VerificationTokenRequest(user_id=user_id, purpose=purpose)
    token_dict = await db[TABLE_NAME].find_one_and_update(
        {'user_id': str(user_id), 'purpose': purpose},
        {'$set': token_req.dict()},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return VerificationToken(**token_dict)


async def verify_verif_token(db: MotorDB, token: VerificationTokenRequest):
    '''Verifies a verification token

    Returns
        VerificationToken: Token is valid
        None: Token is invalid
    '''
    db_token_dict = await db[TABLE_NAME].find_one({'secret': token.secret})
    if db_token_dict:
        # Don't touch tokens which don't belong to the user
        if token.user_id and token.user_id != db_token_dict['user_id']:
            return None

        # Valid secret provided and token belong to user
        # => Delete token
        await db[TABLE_NAME].delete_one({'_id': db_token_dict['_id']})

        # Check if validated for correct purpose
        if token.purpose == db_token_dict['purpose']:
            return VerificationToken(**db_token_dict)
