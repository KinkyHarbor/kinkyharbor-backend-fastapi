from motor import motor_asyncio as motor

from core import settings


client = motor.AsyncIOMotorClient(settings.MONGO_HOST)
db = client.kinkyharbor
