# tasks.py in room app
# from huey_config import huey
from huey.contrib.djhuey import db_task, periodic_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from premailer import transform
from .models import Booking

@db_task()
def send_booking_confirmation_email(booking_id, extended_check_out_date, booking_url):
    try:
        booking = Booking.objects.get(id=booking_id)
        if extended_check_out_date:
            html_content = render_to_string('room/checkout_date_extenstion_email_template.html', {'booking': booking, 'booking_url': booking_url})
        else:
            html_content = render_to_string('room/email_template.html', {'booking': booking, 'booking_url': booking_url})

        html_content = transform(html_content)

        email = EmailMultiAlternatives(
            subject='Room Booking Confirmation',
            from_email='adarhotel33@gmail.com',
            to=[booking.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        print(f"Email sent successfully to {booking.user.email}")

    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist")
    except Exception as e:
        print(f"Error in send_booking_confirmation_email: {e}")
