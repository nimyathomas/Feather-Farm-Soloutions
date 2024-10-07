from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone



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
    address = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'  # Use email to login
    # Fields that are required when creating a user via
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()  # connecting user model with customusermanager
    
    
    def save(self, *args, **kwargs):
        # Check if expiry date exists and is in the past
        if self.expiry_date and self.expiry_date < timezone.now().date():
            self.is_active = False  # Deactivate the user
        super().save(*args, **kwargs)  # Call the base class save method
        
    def __str__(self):
        return self.email
    


    
class SupervisorStakeholderAssignment(models.Model):
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisor_assignments')
    stakeholders = models.ManyToManyField(User, related_name='stakeholder_assignments')

    def __str__(self):
        return f'{self.supervisor.full_name} assigned to {self.stakeholders}'

