'''This module contains test tasks for Celery'''

from harbor.worker.app import app


@app.task
def test_celery(word: str):
    '''Test task for Celery'''
    return f"test task return {word}"
