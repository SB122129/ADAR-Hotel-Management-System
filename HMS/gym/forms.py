# forms.py
from django import forms
from .models import MembershipPlan

class MembershipSignupForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[('chapa', 'Chapa'), ('paypal', 'PayPal')])
