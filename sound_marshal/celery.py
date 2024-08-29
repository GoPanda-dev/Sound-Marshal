from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sound_marshal.settings')

app = Celery('sound_marshal')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

from celery import Celery
from celery.schedules import crontab

app = Celery('sound_marshal')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from core.tasks import refresh_spotify_tokens  # Import the task here
    # Calls refresh_spotify_tokens() every 24 hours
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        refresh_spotify_tokens.s(),
    )