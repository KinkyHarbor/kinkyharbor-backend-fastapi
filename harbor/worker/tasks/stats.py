'''This module contains stats tasks for Celery'''

from harbor.worker.app import app


@app.task
def count_active_users():
    '''Count and store active users'''
