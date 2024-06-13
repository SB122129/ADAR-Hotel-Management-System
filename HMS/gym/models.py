from django.db import models
from dateutil.relativedelta import relativedelta
from django.db import models
from accountss.models import *
from django.urls import reverse

# Create your models here.
class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField()  # Duration of the plan in months
    description = models.TextField()

    def __str__(self):
        return self.name

class Membership(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Additional field to track when the membership was created

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + relativedelta(months=self.plan.duration_months)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class MembershipPayment(models.Model):
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f"Payment for {self.membership.user.username} - {self.membership.plan.name}"