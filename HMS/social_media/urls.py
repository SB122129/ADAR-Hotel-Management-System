# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', ChatBotView.as_view(), name='chat'),
]
