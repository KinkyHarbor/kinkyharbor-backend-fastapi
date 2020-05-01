'''This module contains CRUD operations for verification tokens'''
# pylint: disable=no-member

from bson import ObjectId
from pymongo import ReturnDocument

from harbor.domain.token import VerificationToken, TokenVerifyRequest
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.repository.base import VerifTokenRepo
from harbor.repository.mongo.common import MongoBaseRepo


class VerifTokenMongoRepo(MongoBaseRepo, VerifTokenRepo):
    '''Repository for verification tokens in Mongo'''

    COLLECTION = 'verif_tokens'

    def __init__(self):
        super().__init__()
        self.col = self.db[self.COLLECTION]

    async def __aenter__(self):
        await self.ensure_indexes()
        return self

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index('secret', unique=True)
        await self.col.create_index('created_on', expireAfterSeconds=3600)

    async def create_verif_token(self, user_id: str, purpose: VerifPur) -> VerificationToken:
        # Build token
        token = VerificationToken(user_id=user_id, purpose=purpose)
        token_dict = token.dict(exclude_none=True)
        token_dict['user_id'] = ObjectId(token.user_id)

        # Insert token into DB
        result_dict = await self.col.find_one_and_update(
            {
                'user_id': ObjectId(user_id),
                'purpose': purpose,
            },
            {'$set': token_dict},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return VerificationToken(**result_dict)

    async def verify_verif_token(self, token: TokenVerifyRequest) -> VerificationToken:
        db_token_dict = await self.col.find_one({'secret': token.secret})
        if db_token_dict:
            # Don't touch tokens which don't belong to the user
            if token.user_id and token.user_id != str(db_token_dict['user_id']):
                return None

            # Valid secret provided and token belongs to user
            # => Delete token
            await self.col.delete_one({'_id': db_token_dict['_id']})

            # Check if validated for correct purpose
            if token.purpose == db_token_dict['purpose']:
                return VerificationToken(**db_token_dict)


async def create_repo() -> VerifTokenMongoRepo:
    '''Returns a new instance of the repo'''
    repo = VerifTokenMongoRepo()
    await repo.ensure_indexes()
    return repo
