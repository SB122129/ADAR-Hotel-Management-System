from django.db import models
from accountss.models import Custom_user as User
from django.utils import timezone

class Hall(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Hall_Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hall.name}"
