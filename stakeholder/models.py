from django.db import models
from django.utils import timezone
from user.models import User
from django.db.models import Sum  # Import Sum for aggregation



class ChickBatch(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('uplifted', 'Uplifted'),
        ('terminated', 'Terminated')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chick_batches')
    initial_chick_count = models.IntegerField()  # Initial chick count
    batch_date = models.DateField(default=timezone.now)  # Date the batch started
    duration = models.IntegerField(default=40)  # Duration of the batch in days

    batch_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  # Batch status
    
    def check_batch_completion(self):
        today = date.today()
        end_date = self.batch_date + timedelta(days=self.duration)
        
        # Check if the batch is past its duration and is still active
        if today >= end_date and self.batch_status == 'active':
            self.batch_status = 'completed'
            self.save()

    @property
    def live_chick_count(self):
        """Calculates the current live chick count by subtracting total mortality from the initial chick count."""
        total_mortalities = self.daily_data.aggregate(mortal_sum=models.Sum('mortality_count'))['mortal_sum'] or 0
        return max(0, self.initial_chick_count - total_mortalities)  # Ensure it does not go below zero

    def __str__(self):
        return f"Batch on {self.batch_date} for {self.user.full_name}: {self.initial_chick_count} chicks, {self.live_chick_count} alive"

    def is_coming_soon(self):
        """Checks if a critical event (like a vaccination) is coming soon."""
        return (self.batch_date - timezone.now().date()).days <= 7

    def total_mortality_count(self):
        """Calculate the total mortality count for the batch."""
        return self.daily_data.aggregate(total_mortalities=models.Sum('mortality_count'))['total_mortalities'] or 0

    def average_weight_gain(self):
        """Calculate the average weight gain per chick for the batch."""
        total_weight_gain = self.daily_data.aggregate(total_gain=models.Sum('weight_gain'))['total_gain'] or 0
        total_days = self.daily_data.count()
        return total_weight_gain / total_days if total_days > 0 else 0

    def total_feed_uplifted(self):
        """Calculate the total feed uplifted for the batch."""
        return self.daily_data.aggregate(total_feed=models.Sum('feed_uplifted'))['total_feed'] or 0


class DailyData(models.Model):
    batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE, related_name='daily_data')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_data_records')

    date = models.DateField(default=timezone.now)  # Date for daily record
    alive_count = models.IntegerField()  # Number of chicks still alive on this day
    sick_chicks = models.IntegerField(default=0)  # Number of sick chicks
    weight_gain = models.FloatField()  # Weight gain per chick (in grams)
    feed_uplifted = models.FloatField()  # Amount of feed consumed (in kg)
    water_consumption = models.FloatField()  # Amount of water consumed (in liters)
    temperature = models.FloatField()  # Temperature in the housing environment
    mortality_count = models.IntegerField(default=0)  # Number of chicks that died
    # feed_forecast = models.FloatField(default=0.0)  # You can add this
    # feed_wastage = models.FloatField(default=0.0)  # You can add this
    
    class Meta:
        unique_together = ('batch', 'date')


class FeedMonitoring(models.Model):
    batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE)


    date = models.DateField()
    feed_consumed = models.FloatField(default=0.0)  # Amount of feed consumed (in kg)
    feed_forecast = models.FloatField(default=0.0)  # Predicted feed required for the day (in kg)
    feed_wastage = models.FloatField(default=0.0)  # Amount of feed wasted (in kg)

    def __str__(self):
        return f"Feed Monitoring for Batch {self.batch.batch_date} on {self.date}"
    class Meta:
        verbose_name = "Feed Monitoring"
        verbose_name_plural = "Feed Monitoring"
        unique_together = ('batch', 'date')  # Ensures daily unique entries for each batch
