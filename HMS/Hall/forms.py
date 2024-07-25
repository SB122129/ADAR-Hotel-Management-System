# forms.py

from django import forms
from .models import Hall_Booking
from django import forms
from django.core.exceptions import ValidationError


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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if end_date == start_date:
            if end_time < start_time:
                raise ValidationError("End time cannot be before start time when start and end dates are the same.")
            if end_time == start_time:
                raise ValidationError("End time cannot be the same as start time.")

        return cleaned_data