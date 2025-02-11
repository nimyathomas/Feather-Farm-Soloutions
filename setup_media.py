import os
from django.conf import settings

def setup_media_directories():
    # Create main media directory
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Create QR codes directory
    qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'batch_qr_codes')
    os.makedirs(qr_codes_dir, exist_ok=True)
    
    print(f"Media directories created at: {settings.MEDIA_ROOT}")

# Run this in Django shell:
# from setup_media import setup_media_directories
# setup_media_directories() 