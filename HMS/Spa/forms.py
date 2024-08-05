from django import forms
from django.core.validators import RegexValidator
from .models import SpaBooking, SpaService, SpaPackage

# Validator for first_name and last_name
name_validator = RegexValidator(r'^[a-zA-Z]{2,15}$', 'Only letters are allowed. Must be 2 to 15 characters long.')

# Validator for phone_number
phone_validator = RegexValidator(r'^\+251(9|7)\d{8}$', 'Phone number must be in the format +2519xxxxxxxx or +2517xxxxxxxx.')

class SpaBookingForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    first_name = forms.CharField(
        required=False,
        validators=[name_validator],
        min_length=2,
        max_length=15
    )
    last_name = forms.CharField(
        required=False,
        validators=[name_validator],
        min_length=2,
        max_length=15
    )
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '+2519xxxxxxxx or +2517xxxxxxxx', 'pattern': r'^\+251(9|7)\d{8}$'})
    )
    payment_method = forms.ChoiceField(choices=[('chapa', 'Chapa'), ('paypal', 'PayPal')])

    class Meta:
        model = SpaBooking
        fields = ['service', 'package', 'appointment_date', 'appointment_time', 'for_first_name', 'for_last_name', 'for_email', 'for_phone_number', 'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        booking_for = self.data.get('booking_for')
        
        if booking_for == 'others':
            if not cleaned_data.get('first_name'):
                self.add_error('first_name', 'This field is required for booking for others.')
            if not cleaned_data.get('last_name'):
                self.add_error('last_name', 'This field is required for booking for others.')
            if not cleaned_data.get('email'):
                self.add_error('email', 'This field is required for booking for others.')
            if not cleaned_data.get('phone_number'):
                self.add_error('phone_number', 'This field is required for booking for others.')
