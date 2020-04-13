'''This module contains operations for statistics'''

from pymongo import ASCENDING, DESCENDING

from harbor.domain.stats import Reading
from harbor.repository.base import StatsRepo
from harbor.repository.mongo.common import create_db_client


class StatsMongoRepo(StatsRepo):
    '''Repository for statistics in Mongo'''

    COLLECTION = 'statistics'

    def __init__(self):
        self.client = create_db_client()
        self.col = self.client[self.COLLECTION]

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index([
            ("datetime", DESCENDING),
            ("subject", ASCENDING)
        ], unique=True)

    async def get_latest(self, subject: str) -> Reading:
        '''Returns latest reading for a subject'''
        reading_dict = await self.col.find_one(
            filter={'subject': subject},
            sort=[('datetime', DESCENDING)],
        )

        if reading_dict is not None:
            return Reading(**reading_dict)

    async def set(self, reading: Reading):
        await self.col.find_one_and_update(
            {'datetime': reading.datetime, 'subject': reading.subject},
            {'$set': reading.dict()},
            upsert=True,
        )


async def create_repo() -> StatsMongoRepo:
    '''Returns a new instance of the repo'''
    repo = StatsMongoRepo()
    await repo.ensure_indexes()
    return repo
