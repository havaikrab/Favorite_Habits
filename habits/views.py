from typing import Sequence

from django.db.models import Q, QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsOwner

from .filters import HabitFilterSet, ScheduleFilterSet
from .models import Habit, Schedule
from .paginators import HabitsPaginator
from .serializers import HabitSerializer, ScheduleSerializer


class HabitViewSet(ModelViewSet):
    """Вьюсет для модели привычки"""

    queryset = Habit.objects.all()
    ordering_fields = ["id", "action"]
    search_fields = ["action", "place", "reward"]
    pagination_class = HabitsPaginator
    serializer_class = HabitSerializer
    filterset_class = HabitFilterSet

    def get_queryset(self) -> QuerySet:
        """Разрешение для отображения только собственных привычек пользователя
        и чужих, имеющих положительный признак публикации"""

        queryset = super().get_queryset()
        return queryset.filter(Q(owner=self.request.user) | Q(is_public=True))

    def get_permissions(self) -> Sequence:
        """Определение разрешений на использование функциональности контроллера"""

        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated & IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class ScheduleViewSet(ModelViewSet):
    """Вьюсет для модели расписания"""

    queryset = Schedule.objects.all()
    ordering_fields = ["id", "name"]
    search_fields = ["name"]
    pagination_class = HabitsPaginator
    serializer_class = ScheduleSerializer
    filterset_class = ScheduleFilterSet

    def get_queryset(self) -> QuerySet:
        """Разрешение для отображения только собственных расписаний пользователя"""

        queryset = super().get_queryset()
        return queryset.select_related("habit__owner").filter(habit__owner=self.request.user)

    def get_permissions(self) -> Sequence:
        """Определение разрешений на использование функциональности контроллера"""

        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated & IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
