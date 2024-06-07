import re
import openai
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatBot
from .forms import ChatBotForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Custom_user, ChatMessage
from telegram import Bot
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ChatMessage, Custom_user
from telegram import Bot



import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key="AIzaSyBfK-J0sAekVr5GMfof-QjyiDlcuFCPaO8")

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
        response_text = self.get_gemini_response(user_message)
        
        ChatBot.objects.create(
            user=self.request.user,
            message=user_message,
            response=response_text
        )
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"data": {"text": response_text}})
        return super().form_valid(form)

    def get_gemini_response(self, user_message):
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(user_message)
        
        # Assuming response.text contains the relevant response data
        response_content = response.text
        response_content = response_content.replace("\n", "<br>")
        formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response_content)
        
        return formatted_response



@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        if "message" in data:
            message = data["message"]
            user_id = message["from"]["id"]
            username = message["from"]["username"]
            text = message["text"]

            # Create or get the user
            user, created = Custom_user.objects.get_or_create(telegram_id=user_id, defaults={'username': username})

            # Save the message
            ChatMessage.objects.create(user=user, message=text, timestamp=timezone.now())

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "invalid request"}, status=400)


def send_message_to_telegram(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        message_text = request.POST.get("message")

        user = get_object_or_404(Custom_user, id=user_id)
        telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        telegram_bot.send_message(chat_id=user.telegram_id, text=message_text)
        
        # Save the message in the ChatMessage model
        ChatMessage.objects.create(user=user, message=message_text, timestamp=timezone.now())

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "invalid request"}, status=400)
