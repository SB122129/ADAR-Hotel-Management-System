from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HMS.settings')

app = Celery('HMS')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# myproject/celery.py
app.conf.update(
    worker_hijack_root_logger=False,  # Disable root logger hijack
    worker_redirect_stdouts_level='INFO',
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
