from time import time

from celery import shared_task
from django.core.cache import cache

from config.settings import USE_TELEGRAM_INTEGRATION
from users.services import send_telegram_message, set_tg_webhook

from .services import prepare_events


@shared_task
def scheduled_prepare_events() -> None:
    """Задача по расписанию. Ежеминутно формирует в кеше структуру данных для оповещения пользователей
    о наступлении запланированного события."""

    if USE_TELEGRAM_INTEGRATION:
        set_tg_webhook()
    prepare_events()


@shared_task
def execute_tg_messages_sending() -> None:
    """Задача по расписанию. Выполняет отправку сообщений пользователям через API-telegram"""

    if USE_TELEGRAM_INTEGRATION:
        now_stamp = int(time())
        key = f"messages_at_{now_stamp}"
        messages = cache.get(key)
        if isinstance(messages, dict):
            for k, v in messages.items():
                send_telegram_message(k, v)
