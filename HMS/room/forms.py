from django import forms
from .models import Booking, Payment, RoomRating
from datetime import date
from django import forms
from .models import Booking
from django.core.exceptions import ValidationError

class BookingExtendForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['extended_check_out_date']
        widgets = {
            'extended_check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')
        room_capacity = self.room.capacity

        if guests < 1:
            raise ValidationError('The number of guests must be at least 1.')
        elif guests > room_capacity:
            raise ValidationError(f'The number of guests cannot exceed the room capacity which is {self.room.capacity} for this room.')

        return guests
        

class RoomRatingForm(forms.ModelForm):
    class Meta:
        model = RoomRating
        fields = ['rating', 'review']
from django import forms

