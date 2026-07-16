from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор модели привычки"""

    owner = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        """Параметры сериализатора"""

        model = Habit
        fields = "__all__"

    def validate(self, attrs: dict) -> dict:
        """Проверка передачи взаимоисключающих значений"""

        valid_data: dict = super().validate(attrs)
        is_pleasant = valid_data.get("is_pleasant")
        reward = valid_data.get("reward")
        related_habit = valid_data.get("related_habit")
        if is_pleasant:
            if reward or related_habit:
                raise ValidationError(
                    "Приятная привычка не должна иметь вознаграждения или связанной приятной привычки"
                )
        elif related_habit:
            if reward:
                raise ValidationError(
                    "Привычка не должна одновременно иметь и вознаграждение и связанную приятную привычку"
                )
            if not related_habit.is_pleasant:
                raise ValidationError("Связанная привычка должна быть приятной")
        elif not reward:
            raise ValidationError(
                "Полезная привычка должна поощряться выполнением приятной привычки или вознаграждаться"
            )
        return valid_data
