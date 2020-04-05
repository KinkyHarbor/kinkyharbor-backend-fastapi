'''This module provides common functions to access the database.'''

from motor import motor_asyncio as motor

from harbor.helpers import settings


def create_db_client():
    '''Returns instance of database client'''
    client = motor.AsyncIOMotorClient(settings.MONGO_HOST)
    return client[settings.MONGO_DATABASE]
