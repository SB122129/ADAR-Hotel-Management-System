from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'
