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


class CheckAvailabilityForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}))