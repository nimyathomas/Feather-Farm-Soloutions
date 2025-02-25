from django.db import models
from django.utils import timezone
from user.models import User, Vaccine
from datetime import timedelta, date
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import uuid
import os
import math
from django.core.exceptions import ValidationError
import numpy as np
import cv2
import json
import random



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
    coopcapacity = models.IntegerField(default=0)  # Maximum number of chicks allowed
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
    reward_claimed = models.BooleanField(default=False)
    reward_claimed_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    reward_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Reward amount based on FCR performance"
    )
    reward_status = models.BooleanField(default=False)
    batch_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    qr_code = models.ImageField(upload_to='batch_qr_codes/', blank=True)
 
    # ... your existing fields ...
    total_feed_sacks = models.IntegerField(default=0)
    assigned_feed_sacks = models.IntegerField(default=0)
    remaining_feed_sacks = models.IntegerField(default=0)
    
    # Add these new fields with default values
    starter_feed_consumed = models.IntegerField(default=0)
    grower_feed_consumed = models.IntegerField(default=0)
    finisher_feed_consumed = models.IntegerField(default=0)
    
    # Feed assignment tracking
    starter_feed_sacks = models.IntegerField(
        default=0,
        help_text="Number of starter feed sacks assigned"
    )
    grower_feed_sacks = models.IntegerField(default=0)
    finisher_feed_sacks = models.IntegerField(default=0)

    # Add these new fields
    current_feed_type = models.CharField(
        max_length=50, 
        choices=[
            ('Starter Feed', 'Starter Feed'),
            ('Grower Feed', 'Grower Feed'),
            ('Finisher Feed', 'Finisher Feed')
        ],
        default='Starter Feed'
    )
    last_feed_transition = models.DateTimeField(null=True, blank=True)
    feed_transition_notified = models.BooleanField(default=False)


    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data to QR code
        data = {
            'batch_uuid': str(self.batch_uuid),
            'batch_number': str(self.batch_uuid)[:8],  # First 8 characters of UUID
            'farm_name': self.farm.name if self.farm else 'No Farm',
            'batch_date': self.batch_date.strftime('%Y-%m-%d'),
            'chick_count': self.initial_chick_count,
            'batch_type': self.batch_type
        }
        
        qr.add_data(str(data))
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Create a BytesIO object to temporarily store the image
        stream = BytesIO()
        qr_image.save(stream, 'PNG')
        
        # Create filename using batch UUID
        filename = f'batch_qr_{self.batch_uuid}.png'
        
        # Save the image
        from django.core.files.base import ContentFile
        self.qr_code.save(
            filename,
            ContentFile(stream.getvalue()),
            save=False
        )

    def save(self, *args, **kwargs):
        """Handle all save operations for ChickBatch"""
        # If this is a new batch (no primary key yet)
        if not self.pk:  
            # Generate UUID if not already set
            if not self.batch_uuid:
                self.batch_uuid = uuid.uuid4()
            
            self.available_chickens = self.initial_chick_count
            self.remaining_feed_sacks = self.total_feed_sacks
            
            # Calculate feed requirements based on chick count
            chicks = self.initial_chick_count
            self.total_feed_sacks = (chicks // 100 + (1 if chicks % 100 else 0)) * 6
            self.remaining_feed_sacks = self.total_feed_sacks
            
            # Initialize feed consumption
            self.starter_feed_consumed = 0
            self.grower_feed_consumed = 0
            self.finisher_feed_consumed = 0
            
            # Initialize feed assignments
            self.starter_feed_sacks = 0
            self.grower_feed_sacks = 0
            self.finisher_feed_sacks = 0

        # Generate QR code if it doesn't exist
        if not self.qr_code:
            try:
                self.generate_qr_code()
            except Exception as e:
                print(f"Error generating QR code: {str(e)}")
            
        super().save(*args, **kwargs)

    def check_batch_completion(self):
        today = date.today()
        end_date = self.batch_date + timedelta(days=self.duration)
        if today >= end_date and self.batch_status == "active":
            self.batch_status = "completed"
            self.completion_date = timezone.now()  # Set completion date when batch is completed
            self.save(update_fields=["batch_status", "completion_date"])

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
            # Get total feed consumed from DailyData
            total_feed_consumed = (
                self.daily_data.aggregate(
                    total_feed=models.Sum("feed_uplifted")
                )["total_feed"] or 0.0
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
    
    def get_recommended_feed_type(self):
        """Get recommended feed type based on current week"""
        days_since_start = (timezone.now().date() - self.batch_date).days
        current_week = min((days_since_start // 7) + 1, 6)
        
        if current_week == 1:
            return 'Starter Feed'
        elif 2 <= current_week <= 4:
            return 'Grower Feed'
        else:
            return 'Finisher Feed'

    def check_feed_transition(self):
        """Check and update feed type based on age"""
        new_feed_type = self.get_recommended_feed_type()
        
        if new_feed_type != self.current_feed_type:
            self.current_feed_type = new_feed_type
            self.last_feed_transition = timezone.now()
            self.feed_transition_notified = False
            self.save()
            return True
        return False

    def get_current_feed_type(self):
        current_day = (timezone.now().date() - self.batch_date).days + 1
        if current_day <= 7:
            return 'starter'
        elif current_day <= 28:
            return 'grower'
        else:
            return 'finisher'

    def get_current_feed_assignment(self):
        current_week = ((timezone.now().date() - self.batch_date).days // 7) + 1
        return self.feed_assignments.filter(week_number=current_week).first()

    def get_today_consumption(self):
        today_record = self.daily_feed_records.filter(date=timezone.now().date()).first()
        if today_record:
            return today_record.morning_consumption + today_record.evening_consumption
        return 0

    @property
    def current_day(self):
        return (timezone.now().date() - self.batch_date).days + 1


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
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('qr_scanned', 'QR Scanned'),
        ('evidence_uploaded', 'Evidence Uploaded'),
        ('administered', 'Administered'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ]

    batch = models.ForeignKey(
        ChickBatch, on_delete=models.CASCADE, related_name="vaccination_schedules"
    )
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    vaccination_date = models.DateField()
    assigned_to = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='assigned_vaccinations' ,null=True,  # Allow null temporarily
        blank=True)
    assigned_by = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='created_vaccinations',null=True,  # Allow null temporarily
        blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # QR Code and Verification
    qr_code = models.ImageField(upload_to='vaccination_qr_codes/', blank=True)
    verification_code = models.CharField(max_length=20, unique=True, blank=True)
    
    # Location Verification
    farm_coordinates = models.CharField(max_length=100,null=True,  # Allow NULL in database
        blank=True )  # Format: "latitude,longitude"
    scan_coordinates = models.CharField(max_length=100, blank=True, null=True)
    
    # Evidence Fields
    vaccine_vial_photo = models.ImageField(upload_to='vaccination_evidence/vials/', null=True, blank=True)
    flock_photo = models.ImageField(upload_to='vaccination_evidence/flocks/', null=True, blank=True)
    administration_photo = models.ImageField(upload_to='vaccination_evidence/admin/', null=True, blank=True)
    
    # Environmental Data
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Timestamps and Notes
    created_at = models.DateTimeField(auto_now_add=True )
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    
    
    def generate_verification_code(self):
        """Generate a unique verification code"""
        while True:
            code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            if not VaccinationSchedule.objects.filter(verification_code=code).exists():
                return code

    def generate_qr_code(self):
        """Generate QR code for vaccination"""
        if not self.qr_code:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                
                # Create QR code data
                qr_data = {
                    'verification_code': self.verification_code,
                    'vaccination_id': str(self.pk) if self.pk else '',
                    'batch_id': str(self.batch.id),  # Using auto-generated ID
                    'batch_date': self.batch.batch_date.strftime('%Y-%m-%d'),  # Adding batch start date
                    'vaccine': self.vaccine.name,
                    'date': self.vaccination_date.strftime('%Y-%m-%d')
                }
                
                # Convert to JSON string
                qr_string = json.dumps(qr_data)
                qr.add_data(qr_string)
                qr.make(fit=True)

                # Create QR code image
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Save QR code
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                buffer.seek(0)
                
                filename = f'qr_vaccination_{self.verification_code}.png'
                self.qr_code.save(filename, File(buffer), save=False)
                
            except Exception as e:
                print(f"Error generating QR code: {str(e)}")
                raise

    def save(self, *args, **kwargs):
        """Override save to ensure verification code and QR code"""
        # Generate verification code if not set
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
            
        # Generate QR code if not set
        if not self.qr_code:
            self.generate_qr_code()  # Call the separate method

        super().save(*args, **kwargs)

    def verify_location(self, scan_lat, scan_lng):
        """Verify if the scan location matches the farm location"""
        farm_lat, farm_lng = map(float, self.farm_coordinates.split(','))
        
        # Calculate distance between points (using Haversine formula)
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(farm_lat), radians(farm_lng)
        lat2, lon2 = radians(scan_lat), radians(scan_lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = R * c
        
        # Return True if within 100 meters
        return distance <= 0.1
    def upload_evidence(self, vial_photo, flock_photo, admin_photo, temp, humidity):
        """Upload vaccination evidence"""
        self.vaccine_vial_photo = vial_photo
        self.flock_photo = flock_photo
        self.administration_photo = admin_photo
        self.temperature = temp
        self.humidity = humidity
        self.status = 'evidence_uploaded'
        self.save()

    # def verify_vaccination(self):
    #     """Mark vaccination as verified"""
    #     self.status = 'verified'
    #     self.save()
        
    #     # Create vaccination record
    #     VaccinationRecord.objects.create(
    #         batch=self.batch,
    #         vaccine=self.vaccine,
    #         dose_number=1,  # Assuming single dose
    #         scheduled_date=self.vaccination_date,
    #         administered_date=timezone.now().date(),
    #         status='completed'
    #     )

    def reject_vaccination(self, reason):
        """Reject vaccination with reason"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()

    def __str__(self):
        return f"{self.batch} - {self.vaccine.name} on {self.vaccination_date}"

    

    class Meta:
        ordering = ['-vaccination_date']
        # Update unique constraint to include status
        unique_together = [
            ('batch', 'vaccine', 'vaccination_date', 'status')
        ]

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('fcr', 'FCR Discussion'),
        ('health', 'Health & Safety'),
        ('best_practices', 'Best Practices'),
        ('general', 'General Discussion'),
    ]
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='general'
    )
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



# stakeholder/models.py



class DiseaseAnalysis(models.Model):
    DISEASE_CHOICES = [
        ('healthy', 'Healthy'),
        ('coccidiosis', 'Coccidiosis'),
        ('salmonella', 'Salmonella'),
        ('aspergillosis', 'Aspergillosis'),
        ('colibacillosis', 'Colibacillosis'),
        ('marek', "Marek's Disease"),
        ('newcastle', 'Newcastle Disease'),
        ('infectious_bronchitis', 'Infectious Bronchitis'),
    ]
    CONFIDENCE_LEVELS = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Error', 'Error'),
    ]

    batch = models.ForeignKey(
        ChickBatch, 
        on_delete=models.CASCADE, 
        related_name='disease_analyses'
    )
    image = models.ImageField(
        upload_to='disease_analysis/',
        help_text="Upload image of the chicken for analysis"
    )
    analyzed_date = models.DateTimeField(auto_now_add=True)
    
    # Analysis Results
    predicted_disease = models.CharField(
        max_length=50,
        choices=DISEASE_CHOICES,
        help_text="Predicted disease based on image analysis"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score of the prediction (0-1)"
    )
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    needs_review = models.BooleanField(default=False)

    symptoms_detected = models.JSONField(
        default=list,
        help_text="List of symptoms detected in the analysis"
    )
    warning_message = models.TextField(null=True, blank=True)

    # Additional Analysis Data
    temperature = models.FloatField(
        null=True, 
        blank=True,
        help_text="Body temperature if measured"
    )
    behavior_notes = models.TextField(
        blank=True,
        help_text="Notes about chicken behavior"
    )
    
    # Treatment and Recommendations
    recommendations = models.JSONField(
        default=dict,
        help_text="Treatment recommendations and precautions"
    )
    veterinary_referral = models.BooleanField(
        default=False,
        help_text="Whether veterinary consultation is recommended"
    )
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disease_analyses'
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Indicates if immediate attention is required"
    )
    follow_up_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Recommended date for follow-up analysis"
    )

    class Meta:
        db_table = 'stakeholder_diseaseanalysis'
        ordering = ['-analyzed_date']
        verbose_name = 'Disease Analysis'
        verbose_name_plural = 'Disease Analyses'

    def __str__(self):
        return f"Disease Analysis for Batch {self.batch.id} on {self.analyzed_date.date()}"

    def save(self, *args, **kwargs):
    # Set critical flag based on disease and confidence
        if self.predicted_disease != 'healthy' and self.confidence_score > 0.8:
            self.is_critical = True

        # Generate recommendations based on disease
        self.generate_recommendations()

        # First, save the object so that auto_now_add fields (like analyzed_date) are set.
        super().save(*args, **kwargs)

        # Then, set follow-up date for critical cases if it's not already set.
        if self.is_critical and not self.follow_up_date:
            # Use analyzed_date if available, or fallback to timezone.now()
            analysis_date = self.analyzed_date if self.analyzed_date else timezone.now()
            self.follow_up_date = analysis_date.date() + timezone.timedelta(days=2)
            # Save the update
            super().save(update_fields=["follow_up_date"])  


    def generate_recommendations(self):
        """Generate disease-specific recommendations"""
        recommendations = {
            'treatment_steps': [],
            'preventive_measures': [],
            'isolation_required': False,
            'medication_suggestions': [],
        }
        
        if self.predicted_disease == 'coccidiosis':
            recommendations.update({
                'treatment_steps': [
                    'Administer anticoccidial medication',
                    'Maintain clean and dry litter',
                    'Increase ventilation'
                ],
                'preventive_measures': [
                    'Regular cleaning and disinfection',
                    'Proper litter management',
                    'Avoid overcrowding'
                ],
                'isolation_required': True,
                'medication_suggestions': ['Amprolium', 'Sulfadimethoxine']
            })
        # Add more disease-specific recommendations
        
        self.recommendations = recommendations

    @property
    def severity_level(self):
        """Calculate severity level based on confidence score and disease type"""
        if self.predicted_disease == 'healthy':
            return 'Normal'
        elif self.confidence_score > 0.8:
            return 'High'
        elif self.confidence_score > 0.6:
            return 'Medium'
        else:
            return 'Low'

    def get_similar_cases(self):
        """Find similar disease cases in the same batch"""
        return DiseaseAnalysis.objects.filter(
            batch=self.batch,
            predicted_disease=self.predicted_disease
        ).exclude(id=self.id)

    def should_notify_veterinary(self):
        """Determine if veterinary notification is needed"""
        return (
            self.is_critical or 
            self.confidence_score > 0.9 or 
            self.predicted_disease in ['newcastle', 'marek']
        )
        

class FeedCalculator(models.Model):
    # Constants for feed calculation
    FEED_PER_CHICK_40_DAYS = 4.2  # kg per chick for 40 days
    SACK_WEIGHT = 50  # kg per sack
    
    batch = models.ForeignKey('ChickBatch', on_delete=models.CASCADE)
    number_of_chicks = models.IntegerField()
    calculated_feed_kg = models.FloatField()
    calculated_sacks = models.FloatField()
    safety_margin_sacks = models.FloatField()  # Additional 5% for safety
    
    # Break down by feed types
    starter_feed_sacks = models.FloatField()   # 0-14 days (30%)
    grower_feed_sacks = models.FloatField()    # 15-28 days (35%)
    finisher_feed_sacks = models.FloatField()  # 29-40 days (35%)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def calculate_feed_requirements(number_of_chicks):
        total_feed_kg = number_of_chicks * FeedCalculator.FEED_PER_CHICK_40_DAYS
        base_sacks = total_feed_kg / FeedCalculator.SACK_WEIGHT
        safety_margin = base_sacks * 0.05  # 5% extra
        total_sacks = base_sacks + safety_margin
        
        # Calculate feed type breakdown
        starter_sacks = total_sacks * 0.30   # 30% starter feed
        grower_sacks = total_sacks * 0.35    # 35% grower feed
        finisher_sacks = total_sacks * 0.35  # 35% finisher feed
        
        return {
            'total_feed_kg': total_feed_kg,
            'base_sacks': base_sacks,
            'safety_margin': safety_margin,
            'total_sacks': total_sacks,
            'starter_sacks': starter_sacks,
            'grower_sacks': grower_sacks,
            'finisher_sacks': finisher_sacks
        }
        
class FeedAssignment(models.Model):
    FEED_TYPES = [
        ('Starter Feed', 'Starter Feed'),
        ('Grower Feed', 'Grower Feed'),
        ('Finisher Feed', 'Finisher Feed')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('rejected', 'Rejected')
    ]

    batch = models.ForeignKey('stakeholder.ChickBatch',  # Specify the full path
                             on_delete=models.CASCADE)
    feed_stock = models.ForeignKey('user.FeedStock',  
                                  on_delete=models.CASCADE)
    week_number = models.IntegerField()
    feed_type = models.CharField(max_length=50, choices=FEED_TYPES)
    sacks_assigned = models.IntegerField()
    cost_per_sack = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    is_late = models.BooleanField(default=False)
    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    acknowledgment_date = models.DateTimeField(null=True, blank=True)
    acknowledgment_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feed_assignment'
        unique_together = ['batch', 'week_number']

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new records
            self.total_cost = self.sacks_assigned * self.cost_per_sack
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.batch.id} - Week {self.week_number} - {self.feed_type}" 
    def total_cost(self):
        return self.sacks_assigned * self.cost_per_sack
    
    
    
    
    
class DailyFeedConsumption(models.Model):
    batch = models.ForeignKey('ChickBatch', on_delete=models.CASCADE, related_name='daily_feed_records')
    feed_assignment = models.ForeignKey(FeedAssignment, on_delete=models.CASCADE, related_name='daily_consumptions')
    date = models.DateField()
    day_number = models.IntegerField()
    morning_consumption = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    evening_consumption = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def total_consumption(self):
            """Calculate total daily consumption"""
            return self.morning_consumption + self.evening_consumption
        
    def clean(self):
            """Validate consumption doesn't exceed remaining sacks"""
            total_consumed = self.total_consumption
            current_total = self.feed_assignment.total_consumed
            if total_consumed + current_total > self.feed_assignment.sacks_assigned:
                raise ValidationError(
                    f"Cannot consume {total_consumed} sacks. Only {self.feed_assignment.remaining_sacks} sacks remaining."
                )

    class Meta:
            unique_together = ['batch', 'date']
            ordering = ['-date']
    
    
class VaccinationAuditLog(models.Model):
    vaccination = models.ForeignKey('VaccinationSchedule', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.performed_by} on {self.created_at}"
    
    
def validate_and_save_vial(self, vial_photo, expected_batch_no):
    """
    Validate and save vaccine vial photo
    """
    try:
        # Read image
        img_array = np.frombuffer(vial_photo.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        vial_photo.seek(0)
        
        if img is None:
            raise ValidationError("Unable to process vial image")

        # Validation checks...
        # ... (rest of validation logic) ...

        # If validation passes, save the photo
        self.vaccine_vial_photo = vial_photo  # Changed from empty_vial_photo
        self.save()

        return {
            'success': True,
            'message': 'Vaccine vial validated and saved successfully',
            'details': {
                'fill_level': f"{fill_ratio:.2%}",
                'batch_detected': detected_text,
                'image_quality': f"Blur score: {blur_value:.2f}"
            }
        }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }
    
from django.db import models

class GrowthPrediction(models.Model):
    GROWTH_STATUS_CHOICES = [
        ('On Track', 'On Track'),
        ('Under-Growing', 'Under-Growing'),
        ('Over-Growing', 'Over-Growing'),
        ('Pending', 'Pending Verification')
    ]

    batch = models.ForeignKey('ChickBatch', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    day_number = models.IntegerField()
    feed_consumed = models.FloatField()
    water_consumed = models.FloatField()
    temperature = models.FloatField()
    alive_count = models.IntegerField()
    predicted_weight = models.FloatField()
    actual_weight = models.FloatField(null=True, blank=True)
    weight_difference = models.FloatField(null=True, blank=True)
    growth_status = models.CharField(
        max_length=20, 
        choices=GROWTH_STATUS_CHOICES,
        default='Pending'
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Batch #{self.batch.id} - Day {self.day_number}"
    
    
    