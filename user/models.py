from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models



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
    location = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    plan_file = models.FileField(upload_to='farm_plan/', blank=True, null=True)
    hotel_license = models.FileField(upload_to='hotel_license/', blank=True, null=True)
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
