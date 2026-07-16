from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import CustomUser


class IsOwner(BasePermission):
    """Разрешение для пользователя - владельца"""

    message = "Доступ ограничен. Вы не являетесь владельцем объекта представления."

    def has_object_permission(self, request: Request, view: APIView, obj: CustomUser) -> bool:
        """Проверка, является ли авторизованный пользователь владельцем объекта представления"""

        user = request.user
        return bool(obj == user)
