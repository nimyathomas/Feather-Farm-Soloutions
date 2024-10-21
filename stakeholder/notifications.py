from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
# stakeholder/notifications.py
from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to, body):
    # Initialize Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Send a WhatsApp message
    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f'whatsapp:{to}'  # WhatsApp destination number
    )
    return message.sid