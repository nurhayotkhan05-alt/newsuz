import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import News
from .telegram import send_news_to_telegram

logger = logging.getLogger(__name__)


def _send(news):
    try:
        send_news_to_telegram(news)
    except Exception:
        logger.exception("Telegramga yuborishda kutilmagan xato")


@receiver(post_save, sender=News)
def news_saved(sender, instance, **kwargs):
    if instance.status == 'published' and instance.send_to_telegram:
        transaction.on_commit(lambda: _send(instance))