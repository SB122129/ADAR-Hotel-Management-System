# handlers.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from premailer import transform
from django.dispatch import receiver
from .models import Booking
from .signals import booking_confirmed
from config import BASE_URL

@receiver(booking_confirmed)
def send_booking_confirmation_email(sender, booking, **kwargs):
    booking_url = f"{BASE_URL}/room/my-bookings/"
    if booking.extended_check_out_date:
        html_content = render_to_string('room/checkout_date_extenstion_email_template.html', {'booking': booking, 'booking_url': booking_url})
    else:
        html_content = render_to_string('room/email_template.html', {'booking': booking, 'booking_url': booking_url})
    
    # Inline CSS
    html_content = transform(html_content)
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject='Room Booking Confirmation',
        from_email='adarhotel33@gmail.com',
        to=[booking.user.email]
    )
    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")
    
    # Send the email
    email.send()

    print("Booking confirmation email sent")
