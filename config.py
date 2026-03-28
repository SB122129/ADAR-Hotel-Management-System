# config.py
BASE_URL = 'http://127.0.0.1:8000/'
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_BOT_TOKEN=f'{TOKEN}'
