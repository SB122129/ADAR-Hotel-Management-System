# forms.py

from django import forms
from .models import ChatBot

class ChatBotForm(forms.ModelForm):
    class Meta:
        model = ChatBot
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message here...'}),
        }
