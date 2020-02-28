'''This module handles all ENV and file based settings.'''

import logging
import sys
from os import environ
from pathlib import Path

import aiofiles


def get_required_env(name: str) -> str:
    '''Return a mandatory variable from ENV.'''
    env_var = environ.get(name)
    if not env_var:
        logging.error('%s not defined in ENV', env_var)
        sys.exit(1)
    return env_var


def get_bool(name: str) -> bool:
    '''Return an optional bool from ENV.'''
    value = environ.get(name, 'False')
    return value.lower() == 'true'


# General
DEMO = get_bool('DEMO')
RESERVED_USERNAMES = ['kinkyharbor', 'harbor']

# JWT settings
JWT_KEY_PATH = Path(environ.get('JWT_KEY_PATH', '../jwt-keys'))
JWT_ALG = "ES512"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_jwt_key(key: str):
    '''Return ECDSA keys from files for JWT signing.'''
    filename = f'{key}.pem'
    async with aiofiles.open(JWT_KEY_PATH / filename, mode='r') as f:
        return await f.read()

# Mongo settings
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
MONGO_DATABASE = environ.get('MONGO_DATABASE', 'kinkyharbor')
