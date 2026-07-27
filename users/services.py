import logging
import secrets
from typing import Any

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from config.settings import (
    EMAIL_HOST_USER,
    TG_BOT_ACCESS,
    TG_BOT_LINK_HEAD,
    WEBHOOK_PATH,
)
from users.models import CustomUser

logger = logging.getLogger(__name__)

GREETING = "Привет! Я твой бот-помощник, буду напоминать тебе о твоих привычках."


def set_tg_webhook() -> Any:
    """Передает в API телеграма адрес и токен для взаимодействия с приложением"""

    try:
        url = f"https://api.telegram.org/bot{TG_BOT_ACCESS}/setWebhook?url={WEBHOOK_PATH}"
        response = requests.get(url)
        logger.warning("Статус соединения с API Telegram: %s", response.status_code)
    except Exception as exc:
        logger.error(
            """Ошибка при попытке передать в API Telegram адрес для обратной связи:
        %r.""",
            exc,
        )


def send_tg_bot_link(user: CustomUser, secret: str) -> None:
    """Отправляет зарегистрировавшемуся пользователю ссылку на телеграм-бота приложения"""

    user_link = TG_BOT_LINK_HEAD + f"?start={secret}"
    try:
        send_mail(
            subject="Регистрация в Favorite Habits.",
            message=f"""
Привет, {user.username}, добро пожаловать в Favorite Habits!
Чтобы наш телеграм-бот мог напоминать тебе о твоих любимый привычках,
перейди по ссылке ниже и отправь "/start"
{user_link}
""",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error("Ошибка при обращении к SMTP-серверу: %r.", exc)


def send_telegram_message(chat_id: int, message: str) -> None:
    """Отправляет сообщение пользователю в Telegram"""

    url = f"https://api.telegram.org/bot{TG_BOT_ACCESS}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)  # type: ignore
    except Exception as exc:
        logger.error("Ошибка при отправке сообщения через api.telegram: %r.", exc)


def complete_registration(user: CustomUser) -> None:
    """Сохраняет в БД секретный ключ для идентификации телеграмм-аккаунта пользователя
    и отправляет зарегистрировавшемуся пользователю ссылку на подключение к телеграм-боту"""

    user_secret = secrets.token_urlsafe(12)
    send_tg_bot_link(user, user_secret)
    user.tg_secret = user_secret
    user.save()


def try_add_telegram_chat_id(chat_id: int, message: str) -> None:
    """Совершает попытку добавить объекту пользователя идентификатор телеграм-чата"""

    secret_key = message.replace("/start ", "")
    if len(secret_key) == 16:
        try:
            user = CustomUser.objects.get(tg_secret=secret_key)
        except ObjectDoesNotExist:
            logger.error("Пользователь не найден по секретному ключу")
            respond = "Аккаунт Favorite Habits не обнаружен"
        else:
            if user.tg_chat_id is None:
                user.tg_chat_id = chat_id
                user.save()
            respond = GREETING
        send_telegram_message(chat_id, respond)


def tg_message_handler(data: dict) -> None:
    """Обрабатывает телеграм-сообщения от пользователя"""

    data_message = data.get("message", None)
    if data_message:
        chat_id = data["message"]["chat"]["id"]
        message = data["message"]["text"]
        if "/start " in message:
            return try_add_telegram_chat_id(chat_id, message)
        elif message == "/start":
            respond = GREETING
            send_telegram_message(chat_id, respond)
