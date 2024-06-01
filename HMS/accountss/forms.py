from django import forms
from django.forms import ModelForm  # Import the ModelForm class
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accountss.models import Custom_user
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Custom_user
        fields = ['username', 'first_name', 'last_name','email','phone_number']