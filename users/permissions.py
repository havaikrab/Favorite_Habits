from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from habits.models import Habit, Schedule

from .models import CustomUser


class IsOwner(BasePermission):
    """Разрешение для пользователя - владельца"""

    message = "Доступ ограничен. Вы не являетесь владельцем объекта представления."

    def has_object_permission(self, request: Request, view: APIView, obj: CustomUser | Habit | Schedule) -> bool:
        """Проверка, является ли авторизованный пользователь владельцем объекта представления"""

        user = request.user
        if isinstance(obj, CustomUser):
            return bool(obj == user)
        if isinstance(obj, Habit):
            return bool(obj.owner == user)
        if isinstance(obj, Schedule):
            return bool(obj.habit.owner == user)
        return False
