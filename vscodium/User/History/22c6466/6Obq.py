import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
# app = Celery('app')

# # Using a string here means the worker doesn’t have to serialize
# # the configuration object to child processes
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs
# app.autodiscover_tasks()

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')