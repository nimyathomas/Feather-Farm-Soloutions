from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from math import radians, cos, sin, asin, sqrt
import uuid
from datetime import timedelta
from django.utils import timezone

from .utils import get_full_address_and_region  # Import the utility function



class CustomUserManager(BaseUserManager):

    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


class UserType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)
    user_type = models.ForeignKey(
        UserType, on_delete=models.SET_NULL, null=True, blank=True
    )
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # For nearest calculation

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"  # Use email to login
    # Fields that are required when creating a user via
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()  # connecting user model with customusermanager

    def __str__(self):
        return self.email
    def create_wallet(self):
        from hoteldetails.models import Wallet  # Import here to avoid circular import
        if not hasattr(self, 'wallet'):
            Wallet.objects.create(user=self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_wallet()
    
    


class Supplier(models.Model):
    supplier_code = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )  # Unique supplier code
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255, blank=True, null=True)
    # New field to track active status
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            # Unique supplier code
            models.UniqueConstraint(
                fields=["supplier_code"], name="unique_supplier_code"
            )
        ]

    def __str__(self):
        return self.name


def save(self, *args, **kwargs):
    if not self.region:
        # Get full address and region using the latitude and longitude
        location_data = get_full_address_and_region(self.latitude, self.longitude)
        if location_data:
            self.address = location_data["address"]
            self.region = location_data["region"]

    # Ensure the parent class's save method is called
    super(User, self).save(*args, **kwargs)

    def get_live_chick_counts_and_weights(self):
        """
        Retrieves live chick counts and total weight gain for all ChickBatch instances
        associated with this user.
        """
        batches = self.chick_batches.all()
        results = []

        for batch in batches:
            live_count = batch.live_chick_count  # Get live chick count
            total_weight = batch.total_weight  # Get total weight

            results.append(
                {
                    "batch_date": batch.batch_date,
                    "batch_id": batch.id,
                    "live_chick_count": live_count,
                    "total_weight": total_weight,
                    "batch_status": batch.batch_status,
                }
            )

        return results


class Vaccine(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    vaccination_day = models.IntegerField(choices=[(7, 'Day 7'), (14, 'Day 14'), (21, 'Day 21')])
    current_stock = models.IntegerField(default=0)
    minimum_stock_level = models.IntegerField(default=10)
    doses_required = models.IntegerField(default=1)
    interval_days = models.PositiveIntegerField(default=7)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    VACCINATION_DAY_CHOICES = [
        (7, '7th Day'),
        (14, '14th Day'),
        (21, '21st Day')
    ]
    vaccination_day = models.IntegerField(
        choices=VACCINATION_DAY_CHOICES,
        help_text="Day of vaccination administration"
    )
    doses_required = models.PositiveIntegerField(default=1)
    interval_days = models.PositiveIntegerField()  # Days between doses
    expiry_date = models.DateField(null=True, blank=True)  # Add this field if not present
# New Stock Management Fields
    current_stock = models.PositiveIntegerField(default=0,help_text="Current available stock")# New field for expiry date
    created_at = models.DateTimeField(auto_now_add=True)
    STOCK_STATUS_CHOICES = [
        ('IN_STOCK', 'In Stock'),
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock')
    ]
    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS_CHOICES,
        default='OUT_OF_STOCK'
    )
    minimum_stock_level = models.PositiveIntegerField(
        default=100,
        help_text="Minimum stock level before warning"
    )
    batch_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,  # Allow NULL values
        help_text="Vaccine batch number"
    )

    def update_stock_status(self):
        """Update stock status based on current stock level"""
        if self.current_stock == 0:
            self.stock_status = 'OUT_OF_STOCK'
        elif self.current_stock < self.minimum_stock_level:
            self.stock_status = 'LOW_STOCK'
        else:
            self.stock_status = 'IN_STOCK'
        self.save()

    def save(self, *args, **kwargs):
        # Update stock status before saving
        if self.current_stock == 0:
            self.stock_status = 'OUT_OF_STOCK'
        elif self.current_stock < self.minimum_stock_level:
            self.stock_status = 'LOW_STOCK'
        else:
            self.stock_status = 'IN_STOCK'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class VaccinationRecord(models.Model):
    batch = models.ForeignKey("stakeholder.ChickBatch", on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    dose_number = models.PositiveIntegerField()
    scheduled_date = models.DateField()
    administered_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("completed", "Completed")],
        default="pending",
    )

    def __str__(self):
        return f"{self.batch} - {self.vaccine} - Dose {self.dose_number}"


from django.db import models
from django.core.validators import FileExtensionValidator


class WasteManagementResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ("GUIDE", "Guide"),
            ("VIDEO", "Video"),
            ("ARTICLE", "Article"),
            ("INFOGRAPHIC", "Infographic"),
        ],
    )
    file = models.FileField(
        upload_to="waste_resources/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "mp4", "jpg", "png"]
            )
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DailyTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ("GENERAL", "General"),
            ("COMPOSTING", "Composting"),
            ("RECYCLING", "Recycling"),
            ("WATER", "Water Conservation"),
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BatchPerformanceBenchmark(models.Model):
    PERFORMANCE_LEVEL_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('AVERAGE', 'Average'),
        ('POOR', 'Poor'),
        ('CRITICAL', 'Critical')
    ]

    performance_level = models.CharField(
        max_length=20,
        choices=PERFORMANCE_LEVEL_CHOICES
    )
    
    # Target metrics
    min_weight = models.FloatField()
    max_weight = models.FloatField()
    min_fcr = models.FloatField()
    max_fcr = models.FloatField()
    
    # Environmental conditions
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_humidity = models.FloatField()
    max_humidity = models.FloatField()
    
    # Consumption metrics
    min_feed_intake = models.FloatField()
    max_feed_intake = models.FloatField()
    min_water_consumption = models.FloatField()
    max_water_consumption = models.FloatField()
    
    # Health metrics
    max_mortality_rate = models.FloatField()

    class Meta:
        ordering = ['performance_level']

    @classmethod
    def get_performance_level(cls, 
                            weight, 
                            fcr, 
                            temperature, 
                            humidity,
                            feed_intake,
                            water_consumption,
                            mortality_rate):
        """
        Determines performance level based on current metrics
        """
        benchmarks = cls.objects.all()
        
        for benchmark in benchmarks:
            if (benchmark.min_weight <= weight <= benchmark.max_weight and
                benchmark.min_fcr <= fcr <= benchmark.max_fcr and
                benchmark.min_temperature <= temperature <= benchmark.max_temperature and
                benchmark.min_humidity <= humidity <= benchmark.max_humidity and
                benchmark.min_feed_intake <= feed_intake <= benchmark.max_feed_intake and
                benchmark.min_water_consumption <= water_consumption <= benchmark.max_water_consumption and
                mortality_rate <= benchmark.max_mortality_rate):
                return benchmark.performance_level
                
        return 'CRITICAL'
    
    
    
class FeedStock(models.Model):
    FEED_TYPE_CHOICES = [
        ('starter', 'Starter Feed (0-21 days)'),
        ('grower', 'Grower Feed (22-35 days)'),
        ('finisher', 'Finisher Feed (36+ days)')
    ]
    
    feed_type = models.CharField(max_length=20, choices=FEED_TYPE_CHOICES)
    number_of_sacks = models.PositiveIntegerField(
        help_text="Number of 50kg sacks available"
    )
    price_per_sack = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=1750.00,  # 50kg × ₹35 = ₹1,750
        help_text="Price for one 50kg sack"
    )
    minimum_sacks = models.PositiveIntegerField(
        default=20,
        help_text="Minimum number of sacks to maintain"
    )
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def quantity_in_kg(self):
        """Convert sacks to kilograms"""
        return self.number_of_sacks * 50

    @property
    def price_per_kg(self):
        """Calculate price per kg"""
        return self.price_per_sack / 50

    def get_feed_type_display(self):
        FEED_TYPES = {
            'starter': 'Starter Feed',
            'grower': 'Grower Feed',
            'finisher': 'Finisher Feed'
        }
        return FEED_TYPES.get(self.feed_type, self.feed_type)

    def __str__(self):
        return f"{self.get_feed_type_display()} - {self.number_of_sacks} sacks"
    
# FeatherFarmSoloutions/user/models.py

from django.db import models
from django.conf import settings

class Contract(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending_Admin', 'Pending Admin Signature'),
        ('Pending_Stakeholder', 'Pending Stakeholder Signature'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Terminated', 'Terminated')
    ]

    contract_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_contracts')
    stakeholder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stakeholder_contracts')
    
    # Contract Details
    start_date = models.DateField(default=timezone.now)  # Default to the current date
    end_date = models.DateField(default=timezone.now() + timedelta(days=365))  # Default to one year from now
    contract_type = models.CharField(
        max_length=50,
        choices=[
            ('Standard', 'Standard Contract'),
            ('Premium', 'Premium Contract'),
            ('Special', 'Special Agreement')
        ],
        default='Standard'
    )
    
    # Terms and Conditions
    contract_terms = models.JSONField(default=dict)  # Store structured contract terms
    additional_notes = models.TextField(blank=True)
    
    # Digital Signatures
    admin_signature = models.TextField(blank=True)  # Store base64 signature
    admin_signed_date = models.DateTimeField(null=True, blank=True)
    stakeholder_signature = models.TextField(blank=True)  # Store base64 signature
    stakeholder_signed_date = models.DateTimeField(null=True, blank=True)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contract {self.contract_number} between {self.admin} and {self.stakeholder}"
    
    

class ChatRoom(models.Model):
    farm_name = models.CharField(max_length=255)
    stakeholder = models.ForeignKey('User', on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.farm_name}"

    class Meta:
        ordering = ['-created_at']

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('User', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} - {self.created_at}"


