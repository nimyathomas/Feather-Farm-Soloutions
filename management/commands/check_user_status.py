from django.core.management.base import BaseCommand
from user.models import User

class Command(BaseCommand):
    help = 'Check all users and deactivate if their pollution certificate has expired'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            user.check_certificate_status()
            self.stdout.write(f'Checked {user.email}, is_active: {user.is_active}')
