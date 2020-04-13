'''This module creates a new Celery application'''

from celery import Celery

from harbor.worker import settings

app = Celery(
    "celery",
    broker=f"amqp://guest@{settings.CELERY_RABBITMQ_HOST}//",
    include=['harbor.worker.tasks_test'])

if __name__ == '__main__':
    app.start()
