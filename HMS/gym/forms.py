# forms.py
from django import forms
from .models import Membership

class MembershipSignupForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = []
