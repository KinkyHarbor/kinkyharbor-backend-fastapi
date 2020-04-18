'''This module handles all ENV and file based settings.'''

import logging
from functools import lru_cache
from typing import Set

from pydantic import BaseSettings, AnyHttpUrl, NameEmail, SecretStr, DirectoryPath

from harbor.domain.email import EmailSecurity


class Settings(BaseSettings):
    '''Handles ENV and file based settings'''
    # General
    DEBUG: bool = False
    FRONTEND_URL: AnyHttpUrl = 'http://localhost:3000'
    CORS: Set[AnyHttpUrl] = ['http://localhost:3000']

    # Email
    EMAIL_FROM: NameEmail = 'Kinky Harbor <no-reply@kinkyharbor.com>'
    EMAIL_HOSTNAME: str = 'harbor-smtpd'
    EMAIL_PORT: int = 25
    EMAIL_SECURITY: EmailSecurity = EmailSecurity.UNSECURE
    EMAIL_USERNAME: str = ''
    EMAIL_PASSWORD: SecretStr = ''

    # JWT
    JWT_KEY_PATH: DirectoryPath = 'jwt-keys'
    JWT_ALG: str = "ES512"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Mongo
    MONGO_HOST: str = 'localhost'
    MONGO_DATABASE: str = 'kinkyharbor'


@lru_cache(maxsize=None)
def get_settings():
    '''Returns cached settings object'''
    settings = Settings()

    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    return settings


@lru_cache(maxsize=None)
def get_jwt_key(key: str):
    '''Return ECDSA keys from files for JWT signing.'''
    filename = f'{key}.pem'
    path = get_settings().JWT_KEY_PATH
    with open(path / filename, mode='r') as key_file:
        return key_file.read()
