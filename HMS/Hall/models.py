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


    def __str__(self):
        return self.hall_number

class Hall_Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(default=datetime.time(6, 0),null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hall.name}"
