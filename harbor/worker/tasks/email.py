'''This module contains email tasks for Celery'''

from harbor.worker.app import app


@app.task
def send_mail():
    '''Sends a mail'''
