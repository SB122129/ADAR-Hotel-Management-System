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





# forms.py

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
