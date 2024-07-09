# forms.py

from django import forms
from .models import Hall_Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Hall_Booking
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'amount_due']  # Adjust fields as necessary
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class CheckAvailabilityForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}))