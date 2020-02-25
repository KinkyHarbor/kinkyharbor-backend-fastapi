import logging
import sys
from os import environ


def get_required_env(name: str) -> str:
    env_var = environ.get(name)
    if not env_var:
        logging.error(f'{name} not defined in ENV')
        sys.exit(1)
    return env_var


# JWT settings
JWT_KEY_PRIVATE = get_required_env('JWT_KEY_PRIVATE')
JWT_KEY_PUBLIC = get_required_env('JWT_KEY_PUBLIC')
JWT_ALG = "ES512"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mongo settings
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
