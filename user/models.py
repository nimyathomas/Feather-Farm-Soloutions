from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models 
from math import radians, cos, sin, asin, sqrt

from .utils import get_full_address_and_region  # Import the utility function



class CustomUserManager(BaseUserManager):

    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

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
        UserType, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    

    # ImageField for image uploads
    farm_image = models.ImageField(upload_to='images/', null=True, blank=True)
    length = models.FloatField(default=None, blank=True, null=True)
    breadth = models.FloatField(default=None, blank=True, null=True)
    expiry_date = models.DateField(default=None, blank=True, null=True)
    pollution_certificate = models.FileField(
        upload_to='certificates/', blank=True, null=True)
    coopcapacity = models.IntegerField(default=None, blank=True, null=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)  # New field
    longitude = models.FloatField(blank=True, null=True)  # New field
    region = models.CharField(max_length=100, blank=True, null=True)  # Region field

    address = models.CharField(max_length=255)
    plan_file = models.FileField(upload_to='farm_plan/', blank=True, null=True)
    
    hotel_license = models.FileField(upload_to='hotel_licenses/', blank=True, null=True)
    is_recommended = models.BooleanField(default=False)  # Mark if the farm is recommended
    distance_from_hotel = models.FloatField(blank=True, null=True)  # For nearest calculation
    
    CERTIFICATION_CHOICES = [
        ('ORGANIC', 'Organic Certified'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium Quality'),
    ]
    certification_type = models.CharField(
        max_length=20,
        choices=CERTIFICATION_CHOICES,
        blank=True,
        null=True
    )
    certification_file = models.FileField(upload_to='certifications/', blank=True, null=True)


    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'  # Use email to login
    # Fields that are required when creating a user via
    REQUIRED_FIELDS = ['full_name']
    

    objects = CustomUserManager()  # connecting user model with customusermanager

    def __str__(self):
        return self.email

    def farm_area(self):
        """Calculate the farm area."""
        if self.length and self.breadth:
            return self.length * self.breadth
        return None
    
    
    def calculate_distance_from(self, lat, lon):
        """
        Calculate the distance from this user (farm) to the given latitude and longitude (hotel).
        Uses the Haversine formula to calculate the great-circle distance.
        """
        if self.latitude is None or self.longitude is None:
            return -1  # Return a default value (e.g., -1) if latitude or longitude is missing
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(lat), radians(lon)

        # Haversine formula to calculate distance
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth's radius in kilometers
        km = 6371 * c
        return km

class Supplier(models.Model):
    supplier_code = models.CharField(
        max_length=50, unique=True, blank=True, null=True)  # Unique supplier code
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
                fields=['supplier_code'], name='unique_supplier_code')
        ]

    def __str__(self):
        return self.name

def save(self, *args, **kwargs):
    if not self.region:
        # Get full address and region using the latitude and longitude
        location_data = get_full_address_and_region(self.latitude, self.longitude)
        if location_data:
            self.address = location_data['address']
            self.region = location_data['region']
            
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
            
            results.append({
                'batch_date': batch.batch_date,
                'batch_id':batch.id,
                'live_chick_count': live_count,
                'total_weight': total_weight,
                'batch_status': batch.batch_status,
            })
        
        return results
    

class Vaccine(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    doses_required = models.PositiveIntegerField()
    interval_days = models.PositiveIntegerField()  # Days between doses
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class VaccinationRecord(models.Model):
    batch = models.ForeignKey('stakeholder.ChickBatch', on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    dose_number = models.PositiveIntegerField()
    scheduled_date = models.DateField()
    administered_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
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
            ('GUIDE', 'Guide'),
            ('VIDEO', 'Video'),
            ('ARTICLE', 'Article'),
            ('INFOGRAPHIC', 'Infographic')
        ]
    )
    file = models.FileField(
        upload_to='waste_resources/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'mp4', 'jpg', 'png']
        )]
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
            ('GENERAL', 'General'),
            ('COMPOSTING', 'Composting'),
            ('RECYCLING', 'Recycling'),
            ('WATER', 'Water Conservation')
        ]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    