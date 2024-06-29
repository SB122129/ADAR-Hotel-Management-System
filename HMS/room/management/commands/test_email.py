# yourapp/management/commands/test_email.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Test email sending'

    def handle(self, *args, **kwargs):
        send_mail(
            'Test Email',
            'This is a test email.',
            'adarhotel33@gmail.com',
            ['berhanus771@gmail.com'],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS('Test email sent successfully'))
