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
    
    
class FeedRequest(models.Model):
    FEED_TYPES = [
        ('Pre-Starter', 'Pre-Starter'),
        ('Starter', 'Starter'),
        ('Finisher', 'Finisher'),
    ]
    stakeholder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_requests')
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_feed_requests', null=True, blank=True)
    chick_batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE, related_name='feed_requests')
    feed_amount = models.IntegerField()  # Quantity of feed requested
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES, default='Starter')  # New field for selecting feed type
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"Feed request from {self.stakeholder.full_name} for {self.feed_amount} units"
