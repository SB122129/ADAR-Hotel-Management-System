from django.apps import AppConfig
from django.db.models.signals import post_migrate

class TelegramBotConfig(AppConfig):
    name = 'telegram_bot'

    def ready(self):
        import telegram_bot.signals  # Import signals to connect them
