# project/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Darklight.settings')  # Replace with your project name

app = Celery('Darklight')  # Replace with your project name
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
