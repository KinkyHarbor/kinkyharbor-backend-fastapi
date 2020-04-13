'''Settings for Celery worker'''

from os import environ

CELERY_RABBITMQ_HOST = environ.get('CELERY_RABBITMQ_HOST', 'localhost')
