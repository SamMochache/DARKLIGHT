# tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from .utils.monitoring import SystemMonitor, NetworkMonitor

User = get_user_model()

@shared_task(bind=True, max_retries=3)
def monitor_user_systems(self):
    """Task to monitor all user systems with retry logic"""
    try:
        for user in User.objects.filter(is_active=True):
            SystemMonitor.collect_metrics(user)
    except Exception as e:
        self.retry(exc=e, countdown=60)

@shared_task(bind=True, max_retries=3)
def monitor_network_targets(self):
    """Task to ping common targets for all users"""
    common_targets = ['8.8.8.8', '1.1.1.1']  # Google and Cloudflare DNS
    try:
        for user in User.objects.filter(is_active=True):
            for target in common_targets:
                NetworkMonitor.ping_ip(user, target)
    except Exception as e:
        self.retry(exc=e, countdown=60)