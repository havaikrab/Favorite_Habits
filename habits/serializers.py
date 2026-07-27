from typing import Optional

from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Habit, Schedule
from .services import (
    get_next_with_constant_interval,
    get_next_with_times_in_month,
    get_next_with_times_in_week,
)
from .validators import validate_iso_date_string, validate_month_minutes_list


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор модели привычки"""

    owner = serializers.HiddenField(default=CurrentUserDefault())
    schedule = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Параметры сериализатора"""

        model = Habit
        fields = "__all__"

    def get_schedule(self, habit: Habit) -> Optional[str]:
        """Получение названия расписания"""

        if hasattr(habit, "schedule"):
            return str(habit.schedule.name)
        return None

    def validate(self, attrs: dict) -> dict:
        """Проверка передачи взаимоисключающих значений"""

        current_is_pleasant = None
        current_reward = None
        current_related_habit = None
        user = self.context["request"].user
        if self.instance:
            current_is_pleasant = self.instance.is_pleasant
            current_reward = self.instance.reward
            current_related_habit = self.instance.related_habit
        valid_data: dict = super().validate(attrs)
        is_pleasant = valid_data.get("is_pleasant", current_is_pleasant)
        reward = valid_data.get("reward", current_reward)
        related_habit = valid_data.get("related_habit", current_related_habit)
        if is_pleasant:
            if reward or related_habit:
                raise ValidationError(
                    "Приятная привычка не должна иметь вознаграждения или связанной приятной привычки"
                )
        elif reward and related_habit:
            raise ValidationError("Привычка не должна одновременно иметь и вознаграждение и связанную привычку")
        elif not reward and not related_habit:
            raise ValidationError("У полезной привычки должно быть вознаграждение или связанная приятная привычка")
        elif related_habit:
            if not related_habit.is_pleasant:
                raise ValidationError("Связанная привычка должна быть приятной")
            related_habit_owner = related_habit.owner
            related_is_public = related_habit.is_public
            if user != related_habit_owner and not related_is_public:
                raise PermissionDenied("Чужая непубличная привычка не может быть указана в качестве связанной")
        return valid_data


class ScheduleSerializer(serializers.ModelSerializer):
    """Сериализатор модели расписания"""

    class Meta:
        """Параметры сериализатора"""

        model = Schedule
        exclude = ["next_event"]

    def validate(self, attrs: dict) -> dict:
        """Проверка соответствия значений времени указанному типу расписания"""

        current_start = ""
        current_habit = None
        current_type = None
        current_interval = None
        current_in_week = None
        current_in_month = None
        user = self.context["request"].user
        if self.instance:
            current_start = self.instance.start_at
            current_habit = self.instance.habit
            current_type = self.instance.type
            current_interval = self.instance.constant_interval
            current_in_week = self.instance.times_in_week
            current_in_month = self.instance.times_in_month
        valid_data: dict = super().validate(attrs)
        start_at = valid_data.get("start_at", current_start)
        habit = valid_data.get("habit", current_habit)
        schedule_type = valid_data.get("type", current_type)
        constant_interval = valid_data.get("constant_interval", current_interval)
        times_in_week = valid_data.get("times_in_week", current_in_week)
        times_in_month = valid_data.get("times_in_month", current_in_month)
        validate_iso_date_string(start_at)
        if habit and habit.owner != user:
            raise PermissionDenied("Нельзя назначить расписание для чужой привычки")
        elif schedule_type == "constant_interval":
            if times_in_week or times_in_month or not constant_interval or not 0 <= constant_interval <= 10080:
                raise ValidationError("""
                Для данного типа расписания только одно поле constant_interval
                должно содержать значение от 0 до 10080""")
            valid_data["next_event"] = get_next_with_constant_interval(start_at, constant_interval)
        elif schedule_type == "times_in_week":
            if constant_interval or times_in_month or not isinstance(times_in_week, list):
                raise ValidationError("""
                Для данного типа расписания только одно поле times_in_week
                должно содержать список значений""")
            if len(times_in_week) != len(set(times_in_week)):
                raise ValidationError("Значения в списке times_in_week не должны повторяться")
            for i in times_in_week:
                if not isinstance(i, int) or not 1 <= i <= 10080:
                    raise ValidationError("""
                    Все значения в списке times_in_week должны быть целыми числами от 1 до 10080""")
            valid_data["next_event"] = get_next_with_times_in_week(start_at, times_in_week)
        elif schedule_type == "times_in_month":
            if constant_interval or times_in_week or not isinstance(times_in_month, list):
                raise ValidationError("""
                Для данного типа расписания только одно поле times_in_month
                должно содержать список значений""")
            validate_month_minutes_list(times_in_month)
            valid_data["next_event"] = get_next_with_times_in_month(start_at, times_in_month)
        return valid_data
