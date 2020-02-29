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
        logging.error('%s not defined in ENV', name)
        sys.exit(1)
    return env_var


def get_bool(name: str) -> bool:
    '''Return an optional bool from ENV.'''
    value = environ.get(name, 'False')
    return value.lower() == 'true'


# General
DEMO = get_bool('DEMO')
if DEMO:
    logging.warning('Demo mode activated! Do not use in production!')
RESERVED_USERNAMES = ['kinkyharbor', 'harbor']

# Email settings
EMAIL_FROM_NAME = environ.get('EMAIL_FROM_NAME', 'Kinky Harbor')
EMAIL_FROM_ADDRESS = get_required_env('EMAIL_FROM_ADDRESS')
EMAIL_HOSTNAME = environ.get('EMAIL_HOSTNAME', 'localhost')
EMAIL_PORT = int(environ.get('EMAIL_PORT', '25'))
EMAIL_USERNAME = environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')

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
