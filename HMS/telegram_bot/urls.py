# telegram_bot/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('start-bot/', start_bot, name='start_bot'),
]
