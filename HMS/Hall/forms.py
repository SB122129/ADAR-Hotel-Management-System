# forms.py

from django import forms
from .models import Hall_Booking

class BookingForm(forms.ModelForm):
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)
    start_time = forms.TimeField()
    end_time = forms.TimeField()

    class Meta:
        model = Hall_Booking
        fields = ['start_date', 'end_date', 'start_time', 'end_time']
