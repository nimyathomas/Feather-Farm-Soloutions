from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from user.models import User

class ChickBatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chick_batches')
    chick_count = models.IntegerField()
    batch_date = models.DateField(default=timezone.now)  # Automatically sets the date to the current date when added

    def __str__(self):
        return f"Batch on {self.batch_date} for {self.user.full_name}: {self.chick_count} chicks"
    
    
    def is_coming_soon(self):
        """
        Checks if the vaccination date is within 7 days.
        """
        return (self.batch_date - timezone.now().date()).days == 7
