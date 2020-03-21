'''This module contains CRUD operations for verification tokens'''

from pymongo import ReturnDocument

from harbor.domain.common import ObjectIdStr
from harbor.domain.token import VerificationToken, VerificationTokenRequest
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.repository.mongo.common import create_db_client


class VerificationTokenMongoRepo:
    '''Repository for VerificationTokens in Mongo'''

    COLLECTION = 'verif_tokens'

    def __init__(self):
        client = create_db_client()
        self.col = client[self.COLLECTION]

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index('secret', unique=True)
        await self.col.create_index('created_on', expireAfterSeconds=3600)

    async def create_verif_token(self, user_id: ObjectIdStr, purpose: VerifPur):
        '''Creates and returns a verification token'''
        token_req = VerificationTokenRequest(user_id=user_id, purpose=purpose)
        token_dict = await self.col.find_one_and_update(
            {'user_id': str(user_id), 'purpose': purpose},
            {'$set': token_req.dict()},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return VerificationToken(**token_dict)

    async def verify_verif_token(self, token: VerificationTokenRequest):
        '''Verifies a verification token

        Returns
            VerificationToken: Token is valid
            None: Token is invalid
        '''
        db_token_dict = await self.col.find_one({'secret': token.secret})
        if db_token_dict:
            # Don't touch tokens which don't belong to the user
            if token.user_id and token.user_id != db_token_dict['user_id']:
                return None

            # Valid secret provided and token belong to user
            # => Delete token
            await self.col.delete_one({'_id': db_token_dict['_id']})

            # Check if validated for correct purpose
            if token.purpose == db_token_dict['purpose']:
                return VerificationToken(**db_token_dict)


async def create_repo() -> VerificationTokenMongoRepo:
    '''Returns a new instance of the repo'''
    repo = VerificationTokenMongoRepo()
    await repo.ensure_indexes()
    return repo
