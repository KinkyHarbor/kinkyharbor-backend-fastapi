'''This module creates a new Celery application'''

import logging

from celery import Celery

from harbor.worker import settings

app = Celery(
    "worker",
    broker=f"amqp://guest@{settings.CELERY_RABBITMQ_HOST}//",
    include=[
        'harbor.worker.scheduler',
        'harbor.worker.tasks.email',
        'harbor.worker.tasks.stats',
    ])


def queue_task(task_name, args):
    '''Queue a Celery task'''
    # Log for debugging
    message = 'Add Celery task "%s" to queue with args: %r'
    logging.debug(message, task_name, args)

    # Queue task
    app.send_task(task_name, args=args)

    # Log for debugging
    message = 'Celery task "%s" successfully added to queue'
    logging.debug(message, task_name)


if __name__ == '__main__':
    app.start()
