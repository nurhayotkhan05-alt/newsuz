import requests
from django.conf import settings
from django.urls import reverse
from .models import TelegramLog
import os
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def send_news_to_telegram(news):
    # 1. Takrorni tekshirish: oldin muvaffaqiyatli yuborilgan bo'lsa, to'xtaydi
    if TelegramLog.objects.filter(news=news, is_success=True).exists():
        return False

    # 2. Token sozlanganini tekshirish
    if not settings.TELEGRAM_BOT_TOKEN:
        TelegramLog.objects.create(news=news, is_success=False,
                                   error_msg="TELEGRAM_BOT_TOKEN sozlanmagan")
        return False

    # 3. Matn tuzish
    link = settings.SITE_URL + reverse('article_detail', args=[news.slug])
    text = f"{news.title}\n\n{news.short_description}\n\nBatafsil o'qish: {link}"
    base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
    chat_id = settings.TELEGRAM_CHANNEL_ID

    # 4. Telegram'ga yuborish
    try:
        if news.img:
            with open(news.img.path, 'rb') as photo:
                response = requests.post(
                    f"{base_url}/sendPhoto",
                    data={'chat_id': chat_id, 'caption': text[:1024]},
                    files={'photo': photo},
                    timeout=15,
                )
        else:
            response = requests.post(
                f"{base_url}/sendMessage",
                data={'chat_id': chat_id, 'text': text},
                timeout=15,
            )
        result = response.json()
        if result.get('ok'):
            is_success = True
            error_msg = ''
        else:
            is_success = False
            error_msg = result.get('description', "Noma'lum xato")
    except (requests.RequestException, OSError, ValueError) as e:
        is_success = False
        error_msg = str(e)

    # 5. Logga yozish
    TelegramLog.objects.create(news=news, is_success=is_success, error_msg=error_msg)
    return is_success