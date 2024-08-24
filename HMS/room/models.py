from django.db import models
from django.utils import timezone
from accountss.models import Custom_user 
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.db.models import Q

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name





class Room(models.Model):
    ROOM_STATUS_CHOICES = (
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
    )

    room_number = models.CharField(max_length=20)
    room_type = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    room_status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='vacant')
    room_image = models.ImageField(upload_to='media/room_images/', blank=True)
    capacity = models.IntegerField()
    description = models.TextField(blank=True)
    floor = models.IntegerField()

    def __str__(self):
        return self.room_number

    




class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE, null=True, blank=True) 
    full_name = models.CharField(max_length=100,null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    original_booking_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booking_extend_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    extended_check_out_date = models.DateField(null=True, blank=True)  # New field for extended checkout date
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=True)
    guests = models.IntegerField(null=True, blank=True)
    tx_ref = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def calculate_additional_amount(self):
        if self.extended_check_out_date and self.extended_check_out_date > self.check_out_date:
            extended_days = (self.extended_check_out_date - self.check_out_date).days
            return self.room.price_per_night * extended_days
        else:
            return 0

    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean method to perform validations

        if self.pk is None:  # Only calculate amount if it's a new instance
            # Calculate duration of stay
            duration = (self.check_out_date - self.check_in_date).days
            # Calculate amount based on price per night and duration
            self.original_booking_amount = self.room.price_per_night * duration
        # Perform regular save with validation
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        room = self.room
        super().delete(*args, **kwargs)

    def update_room_and_booking__status(self):
        now = timezone.now().date()
        print(f"Updating room status for room {self.room.room_number}")

        # Check if any booking has check_out_date or extended_check_out_date less than today
        bookings_to_cancel = self.room.booking_set.filter(
            checked_in=True,
            check_out_date__lt=now
        ) | self.room.booking_set.filter(
            checked_in=True,
            extended_check_out_date__lt=now
        )

        if bookings_to_cancel.exists():
            for booking in bookings_to_cancel:
                booking.checked_in = False
                booking.checked_out = True
                booking.status = 'cancelled'
                booking.save()
            self.room.room_status = 'vacant'
        else:
            # Check if any booking has checked_in as True
            if self.room.booking_set.filter(checked_in=True).exists():
                self.room.room_status = 'occupied'
            # Check if any booking has checked_out as True
            elif self.room.booking_set.filter(checked_out=True).exists():
                self.room.room_status = 'vacant'
            else:
                self.room.room_status = 'vacant'

        print(f"Room {self.room.room_number} status updated to {self.room.room_status}")
        self.room.save()
    
    def has_receipt(self):
        return Receipt.objects.filter(booking=self).exists()

    def __str__(self):
        user_display = self.user.username if self.user else self.full_name
        return f"Booking for {user_display} in {self.room} from {self.check_in_date} to {self.check_out_date}"





class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('chapa', 'Chapa'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    )
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt_pdf = models.FileField(upload_to='media/receipts/', blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='chapa')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'completed':
            self.booking.is_paid = True
            self.booking.save()
        elif self.status == 'failed':
            self.booking.delete()

    def __str__(self):
        if self.booking.user:
            user_display = self.booking.user.username
        else:
            user_display = f"{self.booking.full_name}"
        return f"Payment for {user_display} - {self.payment_method}"

class Receipt(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/receipts/')



class RoomRating(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    rating_date = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Booking)
def update_room_and_booking__status(sender, instance, **kwargs):
    instance.update_room_and_booking__status()