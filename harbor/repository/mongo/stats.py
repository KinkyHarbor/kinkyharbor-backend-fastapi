'''This module contains operations for statistics'''

from datetime import datetime, timedelta, timezone, date

from pymongo import ASCENDING, DESCENDING

from harbor.domain.stats import (
    Reading,
    ReadingSubject,
    ReadingAggregation as ReadingAgg,
    ReadingAggregationTimespan as AggTimespan,
    ReadingAggregationOperation as AggOper
)
from harbor.repository.base import StatsRepo
from harbor.repository.mongo.common import MongoBaseRepo


class StatsMongoRepo(MongoBaseRepo, StatsRepo):
    '''Repository for statistics in Mongo'''

    COLLECTION = 'statistics'

    def __init__(self):
        super().__init__()
        self.col = self.db[self.COLLECTION]

    async def __aenter__(self):
        await self.ensure_indexes()
        return self

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index([
            ("datetime", DESCENDING),
            ("subject", ASCENDING)
        ], unique=True)

    async def get_latest(self, subject: ReadingSubject) -> Reading:
        '''Returns latest reading for a subject'''
        reading_dict = await self.col.find_one(
            filter={'subject': subject},
            sort=[('datetime', DESCENDING)],
        )

        if reading_dict is not None:
            return Reading(**reading_dict)

    async def get_by_month(self,
                           subject: ReadingSubject,
                           operation=AggOper.AVERAGE,
                           from_=timedelta(days=-365),
                           to=timedelta()):
        '''Returns aggregated readings for a subject by month'''
        datetime_from = datetime.now(timezone.utc) + from_
        datetime_to = datetime.now(timezone.utc) + to
        pipeline = [
            {'$match': {
                'subject': {'$eq': subject},
                'datetime': {
                    '$gte': datetime_from,
                    '$lte': datetime_to,
                },
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%m.%Y', 'date': "$datetime"}},
                'value': {
                    f'${operation}': "$value",
                }}},
        ]

        # Convert results into dictionary of date and value
        values = {}
        async for doc in self.col.aggregate(pipeline):
            date_parts = doc['_id'].split('.')
            value_date = date(
                day=1,
                month=int(date_parts[0]),
                year=int(date_parts[1]),
            )
            values[value_date] = doc['value']

        # Return ReadingAggregation object
        return ReadingAgg(
            subject=subject,
            timespan=AggTimespan.MONTH,
            operation=AggOper.AVERAGE,
            values=values,
        )

    async def upsert(self, reading: Reading):
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
