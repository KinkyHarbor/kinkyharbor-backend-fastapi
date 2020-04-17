'''This module creates a new Celery application'''

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


if __name__ == '__main__':
    app.start()
