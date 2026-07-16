from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"

    def ready(self) -> None:
        from .services import set_tg_webhook

        set_tg_webhook()
