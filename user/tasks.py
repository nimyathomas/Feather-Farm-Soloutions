# user/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import User


from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta, date


import logging

logger = logging.getLogger(__name__)

@shared_task
def deactivate_expired_users():
    today = timezone.now().date()
    users_to_deactivate = User.objects.filter(expiry_date__lt=today, is_active=True)

    for user in users_to_deactivate:
        user.is_active = False
        user.save()
        print(f"Deactivated user: {user.email}")

    return f"{len(users_to_deactivate)} users deactivated."


@shared_task
def send_expiry_alerts():
    logger.info("Sending expiry alerts...")

    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Retrieve users whose certificates are expiring today and tomorrow
    users_expiring_today = User.objects.filter(expiry_date=today)
    users_expiring_tomorrow = User.objects.filter(expiry_date=tomorrow)

    # Loop through users expiring today
    for user in users_expiring_today:
        if user.email:
            subject = 'Pollution Certificate Expiry Alert'
            message = f'Dear {user.full_name},\n\nYour pollution certificate is expiring today. Please renew it immediately to avoid account deactivation!'
            recipient_list = [user.email]

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                logger.info(f"Sent expiry alert to (today): {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")

    # Loop through users expiring tomorrow
    for user in users_expiring_tomorrow:
        if user.email:
            subject = 'Pollution Certificate Expiry Alert'
            message = f'Dear {user.full_name},\n\nYour pollution certificate is expiring tomorrow. Please renew it to avoid account deactivation!'
            recipient_list = [user.email]

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                logger.info(f"Sent expiry alert to (tomorrow): {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")
                
                
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


@shared_task
def schedule_expiry_alerts():
    # Create or get the Crontab schedule (runs daily at 11:43 AM)

    task_name = 'Send Pollution Certificate Expiry Alerts'
    
    # Get or create the periodic task
    task, created = PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name=task_name,
        task='user.tasks.send_expiry_alerts',
        defaults={
            'kwargs': json.dumps({})  # Pass any arguments if needed
        }
    )

    if created:
        print(f"Scheduled task '{task_name}' created.")
    else:
        print(f"Task '{task_name}' already exists.")

