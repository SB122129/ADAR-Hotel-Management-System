from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from room.models import *
from django import forms
from gym.models import MembershipPlan
class CategoryForm(forms.ModelForm):
    name_regex = RegexValidator(
        regex=r'^[a-zA-Z]{3,10}$',
        message="Name must be 3 to 10 letters long and contain only letters."
    )
    name = forms.CharField(validators=[name_regex])

    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This category name is already exists.")
        return name
    


class RoomForm(forms.ModelForm):
    room_number_regex = RegexValidator(
        regex=r'^[0-9]+$',
        message="Room number must be a positive number"
    )
    room_number = forms.CharField(validators=[room_number_regex])

    def clean_price_per_night(self):
        price_per_night = self.cleaned_data.get('price_per_night')
        if price_per_night < 1:
            raise ValidationError("Price per night must be at least 1.")
        return price_per_night

    def clean_floor(self):
        floor = self.cleaned_data.get('floor')
        if floor < 1:
            raise ValidationError("Floor must be at least 1.")
        return floor

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 1:
            raise ValidationError("Discount must be at least 1.")
        return discount

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if not 1 <= capacity <= 6:
            raise ValidationError("Capacity must be between 1 and 6.")
        return capacity

    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night', 'discount', 'room_image', 'capacity', 'description', 'floor']    


class BookingUpdateForm(forms.ModelForm):
    checked_in = forms.BooleanField(required=False, widget=forms.CheckboxInput)
    checked_out = forms.BooleanField(required=False, widget=forms.CheckboxInput)
    status = forms.ChoiceField(choices=Booking.STATUS_CHOICES, widget=forms.Select)  # Assuming STATUS_CHOICES is defined in your Booking model

    class Meta:
        model = Booking
        fields = ['checked_in', 'checked_out', 'status']

    def clean(self):
        cleaned_data = super().clean()
        checked_in = cleaned_data.get("checked_in")
        checked_out = cleaned_data.get("checked_out")

        if checked_in and checked_out:
            raise ValidationError("Both checked in and checked out cannot be true at the same time.")

        return cleaned_data


from django import forms
from room.models import Booking, Room

class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'full_name', 'check_in_date', 'check_out_date', 'guests']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control rounded'}),
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(room_status='vacant')  # Filter available rooms

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')

        if check_in_date and check_out_date and room:
            if check_out_date <= check_in_date:
                raise forms.ValidationError("Check-out date must be after check-in date.")
        # Additional validation can be added here
        return cleaned_data


class BookingExtendForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['extended_check_out_date']
        widgets = {
            'extended_check_out_date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def clean_extended_check_out_date(self):
        extended_check_out_date = self.cleaned_data.get('extended_check_out_date')
        if extended_check_out_date and extended_check_out_date <= self.instance.check_out_date:
            raise forms.ValidationError("Extended checkout date must be after the current checkout date.")
        return extended_check_out_date


class PaymentCreateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget = forms.Select(choices=Payment.PAYMENT_METHOD_CHOICES)



class PaymentExtendForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

from django import forms
from gym.models import MembershipPlan, Membership, MembershipPayment

class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = '__all__'

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = '__all__'

class MembershipPaymentForm(forms.ModelForm):
    class Meta:
        model = MembershipPayment
        fields = '__all__'



from django import forms
from Hall.models import Hall, Hall_Booking, Hall_Payment

class CheckAvailabilityForm(forms.Form):
    hall = forms.ModelChoiceField(queryset=Hall.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
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
        hall = cleaned_data.get('hall')

        if end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if end_date == start_date and end_time < start_time:
            raise ValidationError("End time cannot be before start time when start and end dates are the same.")

        return cleaned_data

class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'

class HallBookingUpdateForm(forms.ModelForm):
    occupied = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    status = forms.ChoiceField(choices=Hall_Booking.Booking_STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Hall_Booking
        fields = ['occupied', 'status']

    def clean(self):
        cleaned_data = super().clean()
        occupied = cleaned_data.get("occupied")
        status = cleaned_data.get("status")

        if occupied and status == 'cancelled':
            raise forms.ValidationError("Occupied hall cannot have status 'cancelled'.")

        return cleaned_data



class HallBookingForm(forms.ModelForm):
    class Meta:
        model = Hall_Booking
        fields = ['full_name']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hall'].queryset = Hall.objects.all()  # Adjust as necessary

    
class HallPaymentForm(forms.ModelForm):
    class Meta:
        model = Hall_Payment
        fields = '__all__'