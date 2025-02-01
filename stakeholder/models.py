from django.db import models
from django.utils import timezone
from user.models import User, Vaccine
from datetime import timedelta, date
from django.conf import settings



class Farm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="farms")
    farm_image = models.ImageField(
        upload_to="images/", max_length=255, null=True, blank=True
    )
    length = models.FloatField(default=None, blank=True, null=True)
    breadth = models.FloatField(default=None, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    coopcapacity = models.IntegerField(default=None, blank=True, null=True)
    is_recommended = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    plan_file = models.FileField(upload_to="farm_plan/", blank=True, null=True)
    expiry_date = models.DateField(default=None, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    pollution_certificate = models.FileField(
        upload_to="certificates/", blank=True, null=True
    )

    CERTIFICATION_CHOICES = [
        ("ORGANIC", "Organic Certified"),
        ("STANDARD", "Standard"),
        ("PREMIUM", "Premium Quality"),
    ]
    certification_type = models.CharField(
        max_length=20, choices=CERTIFICATION_CHOICES, blank=True, null=True
    )
    certification_file = models.FileField(
        upload_to="certifications/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.length is not None and self.breadth is not None:
            self.size = round(self.length * self.breadth, 2)
        super(Farm, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Owned by {self.owner.get_full_name()}"


class ChickBatch(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("completed", "Completed")]
    TYPE_CHOICES = [("broiler", "Broiler"), ("organic", "Organic"), ("kada", "Kada")]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="farm_user"
    )
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="chick_batches"
    ) 
    initial_chick_count = models.IntegerField(
        help_text="Initial number of chicks in the batch"
    )
    batch_date = models.DateField(
        default=timezone.now, help_text="Date the batch started"
    )
    duration = models.IntegerField(
        default=40, help_text="Duration of the batch in days"
    )
    batch_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current status of the batch",
    )
    batch_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        
        default="broiler",
        help_text="Type of chickens in the batch",
    )

    available_chickens = models.IntegerField(
        help_text="Count of live chickens available", default=0
    )
    batch_size = models.FloatField(
        help_text="Standard weight of a batch (in kg)", default=50.0
    )
    price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price per kg of chicken", null=True
    )
    price_per_batch = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per batch of chicken",
        null=True,
    )

    one_kg_count = models.IntegerField(
        default=0, help_text="Number of 1 kg chickens available"
    )
    two_kg_count = models.IntegerField(
        default=0, help_text="Number of 2 kg chickens available"
    )
    three_kg_count = models.IntegerField(
        default=0, help_text="Number of 3 kg chickens available"
    )
    food_token = models.IntegerField(
        help_text="Reward token for good FCR performance", default=0
    )

    def check_batch_completion(self):
        today = date.today()
        end_date = self.batch_date + timedelta(days=self.duration)
        if today >= end_date and self.batch_status == "active":
            self.batch_status = "completed"
            self.save(update_fields=["batch_status"])

    def calculate_total_profit(total_weight, price_per_kg):
        """
        Calculate the total profit based on total weight and price per kilogram.

        :param total_weight: The total weight of the items in kilograms (float or int)
        :param price_per_kg: The price per kilogram (float or int)
        :return: The total profit (float)
        """
        total_profit = total_weight * price_per_kg
        return total_profit
    
    def update_price_and_tokens(self):
        """
        Update the price per kg and assign food tokens based on FCR performance when the batch is completed.
        """
        if self.batch_status == "completed":
            # Fetch total feed consumed
            total_feed_consumed = (
                FeedMonitoring.objects.filter(batch=self).aggregate(
                    total_feed_consumed=models.Sum("feed_consumed")
                )["total_feed_consumed"]
                or 0.0
            )

            # Calculate FCR based on total feed consumed and total weight
            if self.total_weight > 0:
                fcr = total_feed_consumed / self.total_weight
            else:
                fcr = 0

            # Assign price per kg and tokens based on FCR
            if fcr <= 1.5:
                self.price_per_kg = 10
                self.food_token = 10  # Best performance
            elif 1.5 < fcr <= 1.6:
                self.price_per_kg = 9
                self.food_token = 8
            elif 1.6 < fcr <= 1.7:
                self.price_per_kg = 8
                self.food_token = 5
            else:
                self.price_per_kg = 7
                self.food_token = 2  # Worst performance

            # Save the changes
            self.save(update_fields=["price_per_kg", "food_token"])

    @property
    def live_chick_count(self):
        total_mortalities = (
            self.daily_data.aggregate(mortal_sum=models.Sum("mortality_count"))[
                "mortal_sum"
            ]
            or 0
        )
        return max(0, self.initial_chick_count - total_mortalities)

    @property
    def total_weight(self):
        total_weight_gain = (
            self.daily_data.aggregate(total_gain=models.Sum("weight_gain"))[
                "total_gain"
            ]
            or 0
        )
        return (
            (self.live_chick_count * total_weight_gain) / self.initial_chick_count
            if self.initial_chick_count > 0
            else 0
        )

    def reduce_stock(self, quantity, order_type):
        """Reduce stock based on order type and check availability."""
        if order_type == "kg":
            if self.available_chickens < quantity:
                raise ValueError("Not enough chickens available in stock.")
            self.available_chickens -= quantity
        elif order_type == "batch":
            total_required = quantity * self.batch_size
            if self.available_chickens < total_required:
                raise ValueError(
                    "Not enough chickens available in stock for the requested batches."
                )
            self.available_chickens -= total_required

        self.save(update_fields=["available_chickens"])

    def batch_chicken_price(self):
        weight = self.initial_chick_count * self.total_weight
        if self.price_per_kg and not self.price_per_batch:
            self.price_per_batch = weight * float(self.price_per_kg)
            self.save(update_fields=["price_per_batch"])
        return self.price_per_batch or 0
    
    def save(self, *args, **kwargs):
        if self.batch_status == "completed" and not self.food_token:
            self.update_price_and_tokens()  # Update tokens when batch is completed
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Batch on {self.batch_date} for {self.user.full_name}: {self.initial_chick_count} chicks, {self.live_chick_count} alive"


class DailyData(models.Model):
    batch = models.ForeignKey(
        ChickBatch, on_delete=models.CASCADE, related_name="daily_data"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_data_records"
    )

    date = models.DateField(default=timezone.now)  # Date for daily record
    alive_count = models.IntegerField(help_text="Number of chicks alive on this day")
    sick_chicks = models.IntegerField(default=0, help_text="Number of sick chicks")
    weight_gain = models.FloatField(help_text="Weight gain per chick (in grams)")
    feed_uplifted = models.FloatField(help_text="Feed consumed (in kg)")
    water_consumption = models.FloatField(help_text="Water consumed (in liters)")
    temperature = models.FloatField(help_text="Housing temperature")
    mortality_count = models.IntegerField(
        default=0, help_text="Number of chicks that died"
    )

    class Meta:
        unique_together = ("batch", "date")

    def __str__(self):
        return f"Daily data for {self.batch} on {self.date}"

    def save(self, *args, **kwargs):
        # Save the DailyData record first
        super().save(*args, **kwargs)

        # Update available chickens only if there's mortality
        if self.mortality_count > 0:
            # Prevent recursion by using a flag
            if not getattr(self.batch, "_updating_available_chickens", False):
                print(f"Reducing available chickens by {self.mortality_count}")

                # Set flag to prevent recursion
                self.batch._updating_available_chickens = True

                # Decrease the available chickens
                self.batch.available_chickens -= self.mortality_count

                # Save the updated available chickens count
                self.batch.save(update_fields=["available_chickens"])

                # Clean up the flag after the operation
                del self.batch._updating_available_chickens

    @property
    def total_weight(self):
        """Calculate the cumulative weight gain for the batch on this date."""
        # Sum up weight_gain from all DailyData entries for this batch
        total_weight_gain = (
            self.batch.daily_data.aggregate(total_gain=models.Sum("weight_gain"))[
                "total_gain"
            ]
            or 0
        )
        return total_weight_gain

    def is_coming_soon(self):
        """Checks if a critical event (like a vaccination) is coming soon."""
        return (self.batch.batch_date - timezone.now().date()).days <= 7

    def total_mortality_count(self):
        """Calculate the total mortality count for the batch."""
        return (
            self.batch.daily_data.aggregate(
                total_mortalities=models.Sum("mortality_count")
            )["total_mortalities"]
            or 0
        )

    def average_weight_gain(self):
        """Calculate the average weight gain per chick for the batch."""
        total_weight_gain = (
            self.batch.daily_data.aggregate(total_gain=models.Sum("weight_gain"))[
                "total_gain"
            ]
            or 0
        )
        total_days = self.batch.daily_data.count()
        return total_weight_gain / total_days if total_days > 0 else 0

    def total_feed_uplifted(self):
        """Calculate the total feed uplifted for the batch."""
        return (
            self.batch.daily_data.aggregate(total_feed=models.Sum("feed_uplifted"))[
                "total_feed"
            ]
            or 0
        )


class FeedMonitoring(models.Model):
    batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE)

    date = models.DateField()
    feed_consumed = models.FloatField(default=0.0)
    feed_forecast = models.FloatField(default=0.0)
    feed_wastage = models.FloatField(default=0.0)

    def __str__(self):
        return f"Feed Monitoring for Batch {self.batch.batch_date} on {self.date}"

    class Meta:
        verbose_name = "Feed Monitoring"
        verbose_name_plural = "Feed Monitoring"
        unique_together = ("batch", "date")


class ChickSupply(models.Model):
    batch = models.ForeignKey(
        ChickBatch, on_delete=models.CASCADE, related_name="chick_supplies"
    )
    stakeholder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chick_supplies"
    )  # Link to stakeholder
    date = models.DateField(default=timezone.now)
    chicks_supplied = models.IntegerField(
        help_text="Number of chicks supplied on this day"
    )
    chicken_type = models.CharField(
        max_length=20, choices=ChickBatch.TYPE_CHOICES
    )  # Type of chicken

    def __str__(self):
        return f"Chicks Supplied for Batch {self.batch.batch_date} on {self.date}"


class VaccinationSchedule(models.Model):
    batch = models.ForeignKey(
        ChickBatch, on_delete=models.CASCADE, related_name="vaccination_schedules"
    )
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    vaccination_date = models.DateField()

    def user(self):
        return self.batch.user  # Access user from the related ChickBatch

    def __str__(self):
        return f"{self.batch} - {self.vaccine.name} on {self.vaccination_date}"

class Post(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.owner.email} on {self.post.title}"


# models.py
from django.db import models
from django.conf import settings

class SuccessStory(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="success_stories"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=100,
        choices=[
            ('FCR', 'Improved FCR'),
            ('Scaling Up', 'Successfully Scaling Up'),
            ('Collaboration', 'Collaboration with Hoteliers'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.owner.email}"

class ChickHealthAnalysis(models.Model):
    batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE, related_name='health_analyses')
    image = models.ImageField(upload_to='chick_health_images/')
    analyzed_date = models.DateTimeField(auto_now_add=True)
    
    # Analysis Results
    is_healthy = models.BooleanField()
    status = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    
    # Detailed Metrics
    feather_quality = models.FloatField()
    color_health = models.FloatField()
    overall_condition = models.FloatField()
    
    # Recommendations stored as JSON
    recommendations = models.JSONField()

    def __str__(self):
        return f"Health Analysis for Batch {self.batch.id} on {self.analyzed_date}"

    class Meta:
        ordering = ['-analyzed_date']
        

