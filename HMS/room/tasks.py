from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from premailer import transform

import logging

logger = logging.getLogger(__name__)

@shared_task
def send_confirmation_email(booking_id, base_url):
    from .models import Booking  # Import here to avoid circular import issues
    booking = Booking.objects.get(id=booking_id)
    booking_url = f"{base_url}/room/my-bookings/"
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
    logger.info("Confirmation email sent")
