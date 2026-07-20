from typing import Sequence

from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsOwner

from .filters import HabitFilterSet, ScheduleFilterSet
from .models import Habit, Schedule
from .paginators import HabitsPaginator
from .serializers import HabitSerializer, ScheduleSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Создание новой привычки",
        description="""
Необходима авторизация. Обязательные для заполнения поля: "place", "action", "time_needed".
Пример тела запроса: {"place": "anywhere", "action": "do_some_action", "is_pleasant": false, "reward": "some_reward",
"time_needed": 120, "is_public": true, "related_habit": null}.
Привычка, характеризующаяся как приятная, "is_pleasant": true, иметь вознаграждения или связанной привычки,
но может быть указана, как связанная, для полезной привычки с "is_pleasant": false в поле "related_habit".
Полезная привычка не может иметь одновременно и вознаграждение и связанную полезную привычку.
Продолжительность выполнения привычки не должна превышать 120 секунд.""",
    ),
    list=extend_schema(
        summary="Отображение списка привычек с пагинацией и фильтрацией",
        description="""
Необходима авторизация. Без применения фильтров пользователю отображается список собственных объектов-привычек,
а также привычки, имеющие положительный статус публичности "is_public": true.""",
    ),
    retrieve=extend_schema(
        summary="Отображение деталей привычки",
        description="""
Необходима авторизация. При обращении к объекту, не имеющему положительный статус публичности, или не являющемуся
собственным для пользователя, возвращается ошибка со статус-кодом 403.
В противном случае привычка отображается без ограничений.""",
    ),
    update=extend_schema(
        summary="Полное обновление привычки",
        description="""
Необходима авторизация и права владельца.
В теле запроса необходимо передать обязательные ключи "place", "action", "time_needed" с соответствующими значениями.
При изменении вознаграждения или связанной привычки необходимо "обнулить" несовместимые поля,
иначе будет возвращена ошибка со статус-кодом 400.""",
    ),
    partial_update=extend_schema(
        summary="Частичное обновление привычки",
        description="""
Необходима авторизация и права владельца.
В теле запроса необходимо исключить противоречащие данные, описанные выше для создания или обновления объекта.""",
    ),
    destroy=extend_schema(
        summary="Удаление объекта привычки с привязанным объектом расписания.",
        description="Необходима авторизация и права владельца.",
    ),
)
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


@extend_schema_view(
    create=extend_schema(
        summary="Создание расписания для привычки",
        description="""
Необходима авторизация. Обязательные для заполнения поля: "name", "habit", "type", "start_at".
Пример тела запроса: {"name": "every day", "habit": 5, "type": "constant_interval", "constant_interval": 1440,
"start_at": 2026-07-01T10:00:00Z}. Привычка связана с расписанием отношением "Один к одному". Поле "type" имеет
ограниченный выбор значений: "constant_interval", "times_in_week", "times_in_month". При выборе определенного типа
расписания должно быть заполнено одноименное поле со значением. Значения соответствуют минутам времени.
Примеры данных:
"constant_interval" - число от 1 до 10080, соответствует равным промежуткам времени, каждые n минут;
"times_in_week" - список чисел в диапазоне от 1 до 10080, каждое число соответствует порядковому номеру минуты с начала
текущей недели;
"times_in_month" - список чисел в диапазоне от 1 до 44640, каждое число соответствует порядковому номеру минуты с
начала текущего месяца.
Максимальный интервал между упорядоченными значениями в списке не должен превышать 10080 минут, что соответствует
продолжительности недели. Так как количество минут в месяце - не постоянная величина, следует учитывать,
что минимальное значение в списке "times_in_month" не может превышать 5760, а также в списке должно присутствовать
число от 34560 до 40320. Это условие гарантирует, что при окончании месяца между двумя событиями не пройдет
больше недели.
Для поля "start_at" необходимо передавать строку даты в iso-формате с указанием часового пояса.
Правильное указание часового пояса позволит пользователю своевременно получать оповещения от телеграм-бота.""",
    ),
    list=extend_schema(
        summary="Отображение списка объектов расписаний с пагинацией и фильтрацией",
        description="""
Необходима авторизация. Пользователю отображаются только собственные объекты-расписаний""",
    ),
    retrieve=extend_schema(
        summary="Отображение деталей расписания",
        description="""
Необходима авторизация. При обращении к объекту, не являющемуся собственным для пользователя,
возвращается ошибка со статус-кодом 403. В противном случае расписание отображается без ограничений.""",
    ),
    update=extend_schema(
        summary="Полное обновление расписания",
        description="""
Необходима авторизация и права владельца.
В запросе необходимо передать обязательные ключи "name", "habit", "type", "start_at" со значениями, не противоречащими
условиям, описанным для создания объекта. Важно "обнулять" несовместимые заполненные поля, иначе будет возвращена
ошибка со статус-кодом 400.""",
    ),
    partial_update=extend_schema(
        summary="Частичное обновление расписания",
        description="""
Необходима авторизация и права владельца.
В теле запроса необходимо исключить противоречащие данные, описанные выше для создания или обновления объекта.""",
    ),
    destroy=extend_schema(
        summary="Удаление объекта расписания.",
        description="Необходима авторизация и права владельца.",
    ),
)
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
