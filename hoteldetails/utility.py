from math import radians, sin, cos, sqrt, atan2
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on Earth in kilometers.
    """
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def send_order_confirmation_email(email, order):
    """Send an order confirmation email to the user."""
    subject = f"Order Confirmation - #{order.id}"
    context = {
        "order": order,
        "delivery_date": order.delivery_date,
        "total_price": f"${order.price:.2f}",
        "delivery_option": order.delivery_option,
    }

    # Render email content
    html_message = render_to_string("emails/order_confirmation.html", context)
    plain_message = strip_tags(html_message)
    from_email = "nimyathomas3@gmail.com"  # Use your email address

    send_mail(subject, plain_message, from_email, [email], html_message=html_message)
