from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_order_confirmation(order):
    subject = f"Order Confirmation - #{order.id}"
    message = render_to_string('order_confirmation_email.html', {'order': order})
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
    )
