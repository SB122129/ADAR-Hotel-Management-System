# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', ChatBotViews.as_view(), name='chat'),
    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),
    path('send-message/', send_message_to_telegram, name='send_message_to_telegram'),
]
