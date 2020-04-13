'''This module contains scheduled tasks for Celery'''
# pylint: disable=unused-argument

from celery.schedules import crontab

from harbor.worker.app import app
from harbor.worker.tasks import stats


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    '''Sets periodic tasks for Celery'''

    # Counts active users every night at 01h00
    sender.add_periodic_task(
        crontab(hour=1, minute=0),
        stats.count_active_users,
    )
