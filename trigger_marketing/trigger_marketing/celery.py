# projectname/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trigger_marketing.settings')

# Create a Celery application
app = Celery('trigger_marketing')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks
app.autodiscover_tasks(['trigger_marketing'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
