# forms.py

from django import forms
from .models import Hall_Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Hall_Booking
        fields = ['hall', 'start_date', 'end_date']
