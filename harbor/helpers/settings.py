'''This module handles all ENV and file based settings.'''

import re
import sys
import logging
from typing import List
from os import environ
from pathlib import Path

import aiofiles

from harbor.domain.email import EmailSecurity


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


def get_cors(default_origin: str) -> List[str]:
    '''Gets CORS origins from ENV'''
    cors = environ.get('CORS', default_origin).split(';')
    for origin in cors:
        match = re.search(r'https?://', origin)
        if not match:
            logging.error(
                'CORS origin "%s" doesn\'t start with http(s)', origin)
            sys.exit(1)
    return cors


def get_mail_security(default_sec: EmailSecurity) -> EmailSecurity:
    '''Gets security setting for SMTP'''
    email_sec_env = environ.get('EMAIL_SECURITY', default_sec.value)
    try:
        return EmailSecurity(email_sec_env.lower())
    except ValueError:
        logging.error(
            'Only "tls_ssl", "starttls" and "unsecure" are '
            'valid values for "EMAIL_SECURITY" in ENV')
        sys.exit(1)


# General
DEBUG = get_bool('DEBUG')
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
RESERVED_USERNAMES = ['me', 'kinkyharbor', 'kinky-harbor', 'kinky_harbor', 'harbor',
                      'pirate', 'captain', 'admin', '-', '_']
FRONTEND_URL = environ.get('FRONTEND_URL', 'http://localhost:3000')
CORS = get_cors(FRONTEND_URL)


# Email settings
EMAIL_FROM_NAME = environ.get('EMAIL_FROM_NAME', 'Kinky Harbor')
EMAIL_FROM_ADDRESS = environ.get(
    'EMAIL_FROM_ADDRESS', 'no-reply@kinkyharbor.com')
EMAIL_HOSTNAME = environ.get('EMAIL_HOSTNAME', 'localhost')
EMAIL_PORT = int(environ.get('EMAIL_PORT', '25'))
EMAIL_SECURITY = get_mail_security(EmailSecurity.TLS_SSL)
EMAIL_USERNAME = environ.get('EMAIL_USERNAME')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')

# JWT settings
JWT_KEY_PATH = Path(environ.get('JWT_KEY_PATH', 'jwt-keys'))
JWT_ALG = "ES512"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15


async def get_jwt_key(key: str):
    '''Return ECDSA keys from files for JWT signing.'''
    filename = f'{key}.pem'
    async with aiofiles.open(JWT_KEY_PATH / filename, mode='r') as key_file:
        return await key_file.read()

# Mongo settings
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
MONGO_DATABASE = environ.get('MONGO_DATABASE', 'kinkyharbor')
