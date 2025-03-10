from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_order_confirmation_email(to_email, order):
    subject = "Order Confirmation"
    message = render_to_string('email/order_confirmation.html', {'order': order})
    email = EmailMessage(subject, message, to=[to_email])
    email.send() 