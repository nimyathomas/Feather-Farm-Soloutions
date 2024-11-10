from django.core.mail import send_mail

def send_order_confirmation_email(email, order):
    """
    Send an order confirmation email to the user after placing an order.
    """
    subject = "Order Confirmation - Your order has been placed!"
    message = f"Hello {order.user.full_name},\n\nThank you for your order!\n\n" \
              f"Order Details:\n" \
              f"Order ID: {order.id}\n" \
              f"Total Price: ${order.price}\n" \
              f"Delivery Date: {order.delivery_date}\n" \
              f"Delivery Option: {order.delivery_option.capitalize()}\n\n" \
              "We appreciate your business and will notify you when your order is on the way.\n" \
              "If you have any questions, please feel free to contact us.\n\n" \
              "Best regards,\nTeam Feather Farm Solutions"
    
    send_mail(
        subject,
        message,
        'nimyathomas3@gmail.com',  # Sender's email address
        [email],  # Recipient's email address
        fail_silently=False,
    )