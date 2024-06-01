import re
import openai
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatBot
from .forms import ChatBotForm

openai.api_key = settings.OPENAI_API_KEY

class ChatBotView(LoginRequiredMixin, FormView, ListView):
    model = ChatBot
    form_class = ChatBotForm
    template_name = 'social_media/chat.html'
    success_url = reverse_lazy('chat')
    context_object_name = 'chats'

    def get_queryset(self):
        return ChatBot.objects.filter(user=self.request.user).order_by('timestamp')

    def form_valid(self, form):
        user_message = form.cleaned_data['message']
        response = self.get_gpt3_5_response(user_message)
        
        ChatBot.objects.create(
            user=self.request.user,
            message=user_message,
            response=response
        )
        
        return super().form_valid(form)

    def get_gpt3_5_response(self, user_message):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )
        # Get the response content
        response_content = response.choices[0].message['content']
        # Replace newline characters with HTML line breaks
        response_content = response_content.replace("\n", "<br>")
        # Enclose asterisk-enclosed words in bold tags
        formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response_content)
        return formatted_response
