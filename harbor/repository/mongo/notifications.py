'''This module contains CRUD operations for notifications'''

from datetime import datetime, timezone, timedelta
from typing import List

from bson import ObjectId
from pydantic import parse_obj_as
from pymongo import ASCENDING, DESCENDING

from harbor.domain.notification import Notification
from harbor.repository.base import NotificationRepo
from harbor.repository.mongo.common import MongoBaseRepo


class NotificationMongoRepo(MongoBaseRepo, NotificationRepo):
    '''Repository for notifications in Mongo'''

    COLLECTION = 'notifications'

    def __init__(self):
        super().__init__()
        self.col = self.db[self.COLLECTION]

    async def __aenter__(self):
        await self.ensure_indexes()
        return self

    async def ensure_indexes(self):
        '''Creates required indexes.'''
        await self.col.create_index([
            ("user_id", ASCENDING),
            ("created_on", DESCENDING)
        ])

    async def get_recent(self, user_id: str) -> List[Notification]:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        notif_list = await self.col.find(
            filter={
                'user_id': {'$eq': ObjectId(user_id)},
                '$or': [
                    {'is_read': {'$eq': False}},
                    {'created_on': {'$gte': one_week_ago}},
                ]
            },
            sort=[('created_on', DESCENDING)],
        ).to_list(None)
        return parse_obj_as(List[Notification], notif_list)

    async def get_historic(self, user_id: str, from_: datetime, to: datetime) -> List[Notification]:
        notif_list = await self.col.find(
            filter={
                'user_id': {'$eq': ObjectId(user_id)},
                'created_on': {
                    '$gte': from_,
                    '$lte': to,
                },
            },
            sort=[('created_on', DESCENDING)],
        ).to_list(None)
        return parse_obj_as(List[Notification], notif_list)

    async def get_search(self, user_id: str, search_string: str) -> List[Notification]:
        notif_list = await self.col.find(
            filter={
                'user_id': {'$eq': ObjectId(user_id)},
                '$or': [
                    {'title': {'$regex': f'/.*{search_string}.*/i'}},
                    {'description': {'$regex': f'/.*{search_string}.*/i'}},
                ]
            },
            sort=[('created_on', DESCENDING)],
        ).to_list(None)
        return parse_obj_as(List[Notification], notif_list)

    async def add(self, notification: Notification):
        notif_dict = notification.dict(exclude_none=True)
        notif_dict['user_id'] = ObjectId(notification.user_id)
        await self.col.insert_one(notif_dict)

    async def set_read(self, user_id: str, notif_ids: List[str], value: bool = True) -> int:
        notif_ids = [ObjectId(notif_id) for notif_id in notif_ids]
        result = await self.col.update_many(
            {
                '_id': {'$in': notif_ids},
                'user_id': {'$eq': ObjectId(user_id)},
            },
            {'$set': {'is_read': value}},
        )
        return result.matched_count


async def create_repo() -> NotificationMongoRepo:
    '''Returns a new instance of the repo'''
    repo = NotificationMongoRepo()
    await repo.ensure_indexes()
    return repo
