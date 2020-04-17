'''This module contains scheduled tasks for Celery'''
# pylint: disable=unused-argument

from celery.schedules import crontab

from harbor.worker.app import app
# from harbor.worker.tasks import stats


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'harbor.worker.tasks.stats.count_active_users',
        'schedule': crontab(minute="0", hour="0"),
    },
}


# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     '''Sets periodic tasks for Celery'''
#     # Counts active users every night at 01h00
#     sender.add_periodic_task(
#         schedule=crontab(hour=1, minute=0),
#         task=stats.count_active_users,
#     )

#     # Test task
#     sender.add_periodic_task(
#         schedule=15,
#         task=stats.count_active_users,
#     )
