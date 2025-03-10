from decimal import Decimal
from django.db import models
from stakeholder.models import ChickBatch
from user.models import User
from django.contrib.auth import get_user_model
from decimal import Decimal



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
        choices=[("pending", "Pending"), ("completed", "Completed")],
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
        
        send_order_confirmation_email(self.user.email, self)

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
        return total


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