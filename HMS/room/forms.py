from django import forms
from .models import Booking, Reservation, Payment, RoomRating
from datetime import date

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
        def clean(self):
            cleaned_data = super().clean()
            check_in_date = cleaned_data.get("check_in_date")
            check_out_date = cleaned_data.get("check_out_date")

            # Ensure check-in date is not in the past
            if check_in_date and check_in_date < date.today():
                self.add_error('check_in_date', 'Check-in date cannot be in the past.')

            # Ensure check-out date is not before check-in date
            if check_in_date and check_out_date and check_out_date <= check_in_date:
                self.add_error('check_out_date', 'Check-out date must be after the check-in date.')

            return cleaned_data
        
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in_date', 'check_out_date']


class RoomRatingForm(forms.ModelForm):
    class Meta:
        model = RoomRating
        fields = ['rating', 'review']
from django import forms

