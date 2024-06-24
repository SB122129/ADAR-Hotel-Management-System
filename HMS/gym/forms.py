# forms.py
from django import forms
from .models import MembershipPlan


# forms.py


    

class MembershipSignupForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    subscription_for = forms.ChoiceField(choices=[('self', 'Self'), ('others', 'Others')], widget=forms.RadioSelect)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False)
    payment_method = forms.ChoiceField(choices=[('chapa', 'Chapa'), ('paypal', 'PayPal')])
