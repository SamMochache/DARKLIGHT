from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser

@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = 'Verify Your Email'
        message = f'Hi {user.username}, please verify your email.'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)
    except CustomUser.DoesNotExist as e:
        self.retry(exc=e, countdown=60)