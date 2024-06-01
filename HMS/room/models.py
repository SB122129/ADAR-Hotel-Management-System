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



class RoomManager(models.Manager):
    def available(self):
        now = timezone.now().date()
        return self.filter(
            ~Q(booking__check_in_date__lte=now, booking__check_out_date__gte=now) & 
            ~Q(reservation__check_in_date__lte=now, reservation__check_out_date__gte=now)
        ).distinct()

class Room(models.Model):
    ROOM_STATUS_CHOICES = (
        ('vacant', 'Vacant'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
    )

    room_number = models.CharField(max_length=20)
    room_type = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    room_status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='vacant')
    room_image = models.ImageField(upload_to='media/room_images/', blank=True)
    capacity = models.IntegerField()
    description = models.TextField(blank=True)
    objects = RoomManager()
    floor = models.IntegerField()

    def __str__(self):
        return self.room_number

    def update_room_status(self):
        now = timezone.now()
        if self.booking_set.filter(is_paid=False).exists() or self.reservation_set.filter(check_in_date__gt=now).exists():
            self.room_status = 'reserved'
        elif self.booking_set.filter(is_paid=True, check_out_date__gte=now).exists():
            self.room_status = 'occupied'
        elif not self.booking_set.exists() and not self.reservation_set.filter(check_out_date__gte=now).exists():
            self.room_status = 'vacant'
        self.save()



class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    guests = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        # Ensure check-in date is not in the past
        if self.check_in_date < date.today():
            raise ValidationError('Check-in date cannot be in the past.')

        # Ensure check-out date is not before check-in date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after the check-in date.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean method to perform validations

        if self.pk is None:  # Only calculate amount if it's a new instance
            # Calculate duration of stay
            duration = (self.check_out_date - self.check_in_date).days
            # Calculate amount based on price per night and duration
            self.total_amount = self.room.price_per_night * duration

        super().save(*args, **kwargs)
        self.room.update_room_status()
    def has_receipt(self):
        return Receipt.objects.filter(booking=self).exists()
    def __str__(self):
        return f"Booking for {self.user} in {self.room} from {self.check_in_date} to {self.check_out_date}"

class Receipt(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/receipts/')


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.room.update_room_status()

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'completed':
            self.booking.is_paid = True
            self.booking.save()
        elif self.status == 'failed':
            self.booking.delete()

class RoomRating(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    rating_date = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Booking)
@receiver(post_save, sender=Reservation)
def update_room_status(sender, instance, **kwargs):
    instance.room.update_room_status()