from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Класс представления модели пользователя в админ-панели Django"""

    list_display = ("email", "username", "first_name", "last_name", "tg_name", "tg_chat_id")
    search_fields = ("email", "first_name", "last_name", "tg_name")
