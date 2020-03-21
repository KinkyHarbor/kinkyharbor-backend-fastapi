'''This module contains CRUD operations for refresh tokens'''

from harbor.domain.common import ObjectIdStr
from harbor.domain.token import RefreshToken
from harbor.repository.base import RefreshTokenRepo
from harbor.repository.mongo.common import create_db_client


class RefreshTokenMongoRepo(RefreshTokenRepo):
    '''Repository for refresh tokens in Mongo'''

    COLLECTION = 'refresh_tokens'

    def __init__(self):
        client = create_db_client()
        self.col = client[self.COLLECTION]

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        # Drop refresh token after 3 days of inactivity
        await self.col.create_index('created_on', expireAfterSeconds=3*60*60*24)

    async def create_token(self, user_id: ObjectIdStr) -> RefreshToken:
        token = RefreshToken(user_id=user_id)
        await self.col.insert_one(token.dict())
        return token

    async def replace_token(self, token: RefreshToken) -> RefreshToken:
        db_token_dict = await self.col.find_one_and_delete({
            'secret': token.secret,
            'user_id': token.user_id
        })

        if db_token_dict:
            # Valid token found, create new token
            return await self.create_token(token.user_id)


async def create_repo() -> RefreshTokenMongoRepo:
    '''Returns a new instance of the repo'''
    repo = RefreshTokenMongoRepo()
    await repo.ensure_indexes()
    return repo
