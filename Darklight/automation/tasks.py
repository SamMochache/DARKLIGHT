# tasks.py - Update to use modern async Celery
from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import check_and_apply_rules
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def evaluate_automation_rules(self):
    try:
        for user in User.objects.all():
            check_and_apply_rules(user)
    except Exception as e:
        logger.error(f"Automation rule evaluation failed: {str(e)}")
        raise self.retry(exc=e)