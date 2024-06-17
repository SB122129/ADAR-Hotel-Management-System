# forms.py
from django import forms
from .models import MembershipPlan

class MembershipSignupForm(forms.Form):
    plan_id = forms.IntegerField(widget=forms.HiddenInput())
    payment_method = forms.ChoiceField(choices=[('chapa', 'Chapa'), ('paypal', 'PayPal')])
