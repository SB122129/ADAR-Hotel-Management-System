from django.db.models.signals import post_migrate
from django.dispatch import receiver
import requests
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def start_bot(sender, **kwargs):
    try:
        response = requests.get('https://alyz1358fq6u.share.zrok.io/telegram/start-bot/')
        logger.info(f"start_bot response: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error calling start-bot URL: {e}")
