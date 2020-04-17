'''This module provides common functions to access the database.'''

import asyncio
from abc import ABC, abstractmethod

from motor import motor_asyncio as motor

from harbor.helpers.settings import get_settings


def create_db_client():
    '''Returns instance of database client'''
    return motor.AsyncIOMotorClient(get_settings().MONGO_HOST)


def get_default_db(client: motor.AsyncIOMotorClient):
    '''Returns client for default database'''
    return client[get_settings().MONGO_DATABASE]


class MongoBaseRepo(ABC):
    '''Base class for Mongo repositories'''

    def __init__(self):
        self.client = create_db_client()
        self.db = get_default_db(self.client)

    @abstractmethod
    async def __aenter__(self):
        pass

    async def close(self):
        '''Closes client connection'''
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.client.close)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
