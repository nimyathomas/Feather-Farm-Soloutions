from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

def ready(self):
        from .tasks import schedule_expiry_notification_task
        schedule_expiry_notification_task()