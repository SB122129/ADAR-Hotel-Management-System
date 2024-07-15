from django.db import models
from accountss.models import Custom_user as User
from django.utils import timezone
import datetime

class Hall_Category(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Hall(models.Model):
    Hall_STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
    )
    hall_type = models.ForeignKey(Hall_Category, on_delete=models.CASCADE, default=1)
    hall_number = models.CharField(max_length=20, default='000')
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    image = models.ImageField(upload_to='media/hall_images/', blank=True)
    floor = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Hall_STATUS_CHOICES, default='available')


    def __str__(self):
        return self.hall_number

class Hall_Booking(models.Model):
    Booking_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(default=datetime.time(6, 0),null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    tx_ref = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Booking_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.hall.hall_type}"




class Hall_Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('chapa', 'Chapa'),
        ('paypal', 'PayPal'),
    )
    booking = models.OneToOneField(Hall_Booking, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='chapa')
    
    def __str__(self):
        return f"Payment {self.id} - {self.status}"