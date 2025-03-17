from decimal import Decimal
from django.db import models
from stakeholder.models import ChickBatch
from user.models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  # Import settings here
from .utils import send_order_confirmation_email  # Adjust the path as necessary
from django.utils import timezone
from datetime import datetime, timedelta  # Add this import
# Add this import




class HotelUser(models.Model):
    hotel_name = models.CharField(max_length=100)
    hotel_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hotel_users"
    )
    expiry_date = models.DateField(default=None, blank=True, null=True)
    hotel_license = models.FileField(upload_to="hotel_licenses/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)  # New field for latitude
    longitude = models.FloatField(blank=True, null=True)  # New field for longitude

    def get_hotel_name(self):
        """fetch the hotel name from obj"""
        return self.hotel_name

    def __str__(self):
        return f"{self.hotel_owner.full_name}'s Hotel - {self.address or 'No Address'}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE)

    # Quantities ordered by the hotel for different weights
    one_kg_count = models.IntegerField(
        default=0, help_text="Number of 1 kg chickens ordered"
    )
    two_kg_count = models.IntegerField(
        default=0, help_text="Number of 2 kg chickens ordered"
    )
    three_kg_count = models.IntegerField(
        default=0, help_text="Number of 3 kg chickens ordered"
    )

    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(
        null=True, blank=True, help_text="Expected delivery date"
    )
    price = models.DecimalField(
        max_digits=10,
        
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total order price",
    )
    payment_method = models.CharField(
        max_length=10,
        choices=[
            ("cod", "Cash On Delivery"),
            ("online", "Online Transfer"),
            ("upi", "UPI"),
        ],
        default="cod",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"),
                 ("completed", "Completed"),
                  ('transit_to_hotel', 'Transit to Hotel'),  # New status
                  ('out_for_delivery', 'Out for Delivery'),
                  ('delivered', 'Delivered'),
                  ('cancelled', 'Cancelled'),
                  ('rejected', 'Rejected')],
        default="pending",
    )

    DELIVERY_OPTIONS = [
        ("standard", "Standard Delivery"),
        ("express", "Express Delivery"),
    ]
    delivery_option = models.CharField(
        max_length=10, choices=DELIVERY_OPTIONS, default="standard"
    )
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Fee based on delivery option",
    )
    
    admin_notes = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)  # Add this field

    last_location_update = models.DateTimeField(null=True, blank=True)
    transit_started_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)  #
    
    tracking_token = models.CharField(max_length=64, null=True, blank=True)


    def send_status_notification(self):
        subject = f"Order #{self.id} Status Update"
        message = render_to_string('hoteldetials/email/order_status_update.html', {
            'order': self,
            'status': self.get_status_display()
        })
        
        # Send email to hotelier
        send_mail(
            subject=subject,
            message='',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            html_message=message
        )

    def calculate_delivery_fee(self):
        if self.delivery_option == "express":
            return Decimal("1000.00")  # Set the express delivery fee
        return Decimal("0.00")  # No fee for standard delivery

    def save(self, *args, **kwargs):
        self.delivery_fee = self.calculate_delivery_fee()
        super().save(*args, **kwargs)
        
    def can_fulfill_order(self):
        # Get the batch associated with this order
        batch = self.batch
        
        # Check if we have enough chickens of each weight category
        if (self.one_kg_count <= batch.one_kg_count and 
            self.two_kg_count <= batch.two_kg_count and 
            self.three_kg_count <= batch.three_kg_count):
            return True
        return False

    def confirm_order(self):
        if not self.can_fulfill_order():
            raise ValueError("Not enough chickens available to fulfill this order.")

        # Update the batch quantities
        batch = self.batch
        batch.one_kg_count -= self.one_kg_count
        batch.two_kg_count -= self.two_kg_count
        batch.three_kg_count -= self.three_kg_count
        
        # Update available chickens count
        batch.available_chickens = (
            batch.one_kg_count + 
            batch.two_kg_count + 
            batch.three_kg_count
        )
        
        # Update status
        self.status = 'confirmed'
        
        # Save changes
        batch.save()
        self.save()
        
        # Send confirmation email
        

    def total_weight(self):
        """Calculate the total weight of the order."""
        return (
            (self.one_kg_count * 1)
            + (self.two_kg_count * 2)
            + (self.three_kg_count * 3)
        )

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"
    
    def total_price(self):
        total = Decimal("0.00")
        cart_items = CartItem.objects.filter(cart__user=self.user)
        for item in cart_items:
            total += item.total_price()  # Assuming each CartItem has a method total_price()
    def start_transit(self):
        if self.status == 'confirmed':
            self.status = 'transit_to_hotel'
            
            # Set initial location to farm location
            self.current_latitude = self.batch.farm.latitude
            self.current_longitude = self.batch.farm.longitude
            
            # Set transit start time based on delivery date and option
            if self.delivery_option == 'express':
                # For express delivery, start immediately
                self.transit_started_at = timezone.now()
            else:
                # For standard delivery, start on delivery date
                delivery_datetime = datetime.combine(
                    self.delivery_date, 
                    datetime.min.time()
                ).replace(hour=8)  # Start at 8 AM on delivery date
                self.transit_started_at = delivery_datetime
                
            self.save()
            return True
        return False
    def initialize_location(self):
        """Initialize current location with farm coordinates"""
        if self.current_latitude is None or self.current_longitude is None:
            self.current_latitude = self.batch.farm.latitude
            self.current_longitude = self.batch.farm.longitude
            self.last_location_update = timezone.now()
            self.save()

    def update_location(self, latitude, longitude):
        """Update current location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save()

    def complete_delivery(self):
        """Mark order as delivered"""
        if self.status == 'transit_to_hotel':
            self.status = 'delivered'
            self.delivered_at = timezone.now()
            self.save()
            return True
        return False


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"cart of {self.user.full_name}"

    def get_farm_address(self):
        farm = self.user.farms.first()  # Assuming each user has at least one farm
        return farm.address if farm else "No farm address available"


class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [("live", "Live"), ("processed", "Processed")]
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    chick_batch = models.ForeignKey(ChickBatch, on_delete=models.CASCADE)

    # New fields for weight categories
    one_kg_count = models.IntegerField(
        default=0, help_text="Number of 1 kg chickens ordered"
    )
    two_kg_count = models.IntegerField(
        default=0, help_text="Number of 2 kg chickens ordered"
    )
    three_kg_count = models.IntegerField(
        default=0, help_text="Number of 3 kg chickens ordered"
    )
    is_processed = models.BooleanField(
        default=False, help_text="True if fully dressed, False if live"
    )

    item_type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES,
        default="live",
        help_text="Specify if the item is live or processed",
    )
    # Additional cost per chicken when processed
    ADDITIONAL_PROCESSED_COST = Decimal("5.00")

    def total_price(self):
        """
        Calculate the total price, including weight-based pricing and additional costs for processing.
        """
        one_kg_count = self.one_kg_count or 0
        two_kg_count = self.two_kg_count or 0
        three_kg_count = self.three_kg_count or 0
        price_per_kg = self.chick_batch.price_per_kg or Decimal("0.00")

        # Base price based on weight categories and price per kg
        base_price = (
            (one_kg_count * price_per_kg)
            + (two_kg_count * 2 * price_per_kg)
            + (three_kg_count * 3 * price_per_kg)
        )

        # Total count of chickens
        total_chickens = one_kg_count + two_kg_count + three_kg_count

        # Add additional processing cost if processed
        if self.is_processed:
            processing_cost = total_chickens * self.ADDITIONAL_PROCESSED_COST
            return base_price + processing_cost

        return base_price

    @property
    def discounted_price(self):
        """Calculates the price after a 5% discount."""
        discount = Decimal("0.10") * self.total_price()
        return self.total_price() - discount

    def __str__(self):
        return f"CartItem of {self.cart.user.email} - {self.chick_batch} ({self.item_type})"

User = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loyalty_points = models.IntegerField(default=0)
    membership_tier = models.CharField(max_length=20, default='Silver', choices=[
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user.get_full_name()} (Balance: ₹{self.balance})"
    
    def add_funds(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.balance += Decimal(amount)
        self.save()
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='credit',
            description=f"Added funds: ₹{amount}"
        )

    def deduct_funds(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if self.balance < amount:
            raise ValueError("Insufficient balance.")
        self.balance -= Decimal(amount)
        self.save()
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='debit',
            description=f"Deducted funds: ₹{amount}"
        )

    def add_loyalty_points(self, points):
        if points <= 0:
            raise ValueError("Points must be greater than zero.")
        self.loyalty_points += points
        self.save()

    def upgrade_membership(self):
        if self.loyalty_points >= 1000 and self.membership_tier != 'Platinum':
            self.membership_tier = 'Platinum'
        elif self.loyalty_points >= 500 and self.membership_tier != 'Gold':
            self.membership_tier = 'Gold'
        self.save()
        
        
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS,
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"{self.transaction_type.title()} of ₹{self.amount} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']