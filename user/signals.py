from django.utils import timezone

class User(AbstractUser):
    # Your existing fields...

    def check_certificate_status(self):
        """Check if the pollution certificate is still valid."""
        if self.expiry_date and self.expiry_date < timezone.now().date():
            # Expiry date has passed, make the user inactive
            self.is_active = False
        else:
            # Expiry date is valid, make the user active
            self.is_active = True
        self.save()

    def renew_certificate(self, new_expiry_date):
        """Renew the pollution certificate by updating the expiry date and activating the user."""
        self.expiry_date = new_expiry_date
        self.is_active = True
        self.save()
