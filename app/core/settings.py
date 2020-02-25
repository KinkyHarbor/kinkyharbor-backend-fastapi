import logging
import sys
from os import environ
from pathlib import Path

import aiofiles


def get_required_env(name: str) -> str:
    env_var = environ.get(name)
    if not env_var:
        logging.error(f'{name} not defined in ENV')
        sys.exit(1)
    return env_var


# JWT settings
JWT_KEY_PATH = Path('../jwt-keys')
JWT_ALG = "ES512"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_jwt_key(key: str):
    async with aiofiles.open(JWT_KEY_PATH / f'{key}.pem', mode='r') as f:
        return await f.read()

# Mongo settings
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
