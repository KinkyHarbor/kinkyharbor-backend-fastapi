'''This module provides common functions to access the database.'''
from motor import motor_asyncio as motor

from core import settings


def get_db():
    '''Returns instance of database client'''
    client = motor.AsyncIOMotorClient(settings.MONGO_HOST)
    return client[settings.MONGO_DATABASE]
