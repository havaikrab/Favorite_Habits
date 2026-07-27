from django.apps import AppConfig

from config.settings import USE_TELEGRAM_INTEGRATION


class UsersConfig(AppConfig):
    name = "users"

    def ready(self) -> None:

        if USE_TELEGRAM_INTEGRATION:
            from .services import set_tg_webhook

            set_tg_webhook()
