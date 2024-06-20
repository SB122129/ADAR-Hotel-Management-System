from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from telegram import Update
import asyncio

logger = logging.getLogger(__name__)

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your bot.")

class Command(BaseCommand):
    help = 'Starts the Telegram bot.'

    def handle(self, *args, **options):
        async def main():
            application = Application.builder().token(TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            await application.run_polling()

        asyncio.run(main())
