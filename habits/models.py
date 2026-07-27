from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import CustomUser


class Habit(models.Model):
    """Модель привычки"""

    owner: models.ForeignKey = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="habits", verbose_name="Владелец"
    )
    place: models.CharField = models.CharField(verbose_name="Место выполнения привычки")
    action: models.CharField = models.CharField(verbose_name="Действие привычки")
    is_pleasant: models.BooleanField = models.BooleanField(
        verbose_name="Признак приятной привычки", blank=True, default=False
    )
    related_habit: models.ForeignKey = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="required_habits",
        verbose_name="Связанная приятная привычка",
        null=True,
    )
    reward: models.CharField = models.CharField(verbose_name="Вознаграждение", null=True)
    time_needed: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="Время на выполнение привычки",
        validators=[
            MinValueValidator(1, message="Продолжительность привычки не может быть меньше секунды."),
            MaxValueValidator(120, message="Продолжительность привычки не может быть больше 120 секунд."),
        ],
    )
    is_public: models.BooleanField = models.BooleanField(verbose_name="Признак публичности", blank=True, default=False)

    class Meta:
        """Класс настроек отображения"""

        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["action", "is_public"]

    def __str__(self) -> str:
        """Строковое отображение объекта урока"""

        return str(self.action)


class Schedule(models.Model):
    """Модель расписания"""

    name: models.CharField = models.CharField(verbose_name="Название")
    habit: models.OneToOneField = models.OneToOneField(
        Habit, on_delete=models.CASCADE, related_name="schedule", verbose_name="Привычка"
    )
    TYPE_CHOICES = [
        ("constant_interval", "Равные промежутки времени"),
        ("times_in_week", "Несколько раз в неделю"),
        ("times_in_month", "Несколько раз в месяц"),
    ]
    type: models.CharField = models.CharField(max_length=17, choices=TYPE_CHOICES, verbose_name="Тип расписания")
    constant_interval: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name="Постоянный интервал в минутах",
        validators=[
            MinValueValidator(1, message="Значение не может быть меньше 1 минуты"),
            MaxValueValidator(10080, message="Значение не может быть больше 10080 минут"),
        ],
        null=True,
    )
    times_in_week: models.JSONField = models.JSONField(
        verbose_name="Список значений в минутах в течение недели", null=True
    )
    times_in_month: models.JSONField = models.JSONField(
        verbose_name="Список значений в минутах в течение месяца", null=True
    )
    start_at: models.CharField = models.CharField(verbose_name="Начало отсчета времени", max_length=32)
    next_event: models.BigIntegerField = models.BigIntegerField(verbose_name="Следующее событие")

    class Meta:
        """Класс настроек отображения"""

        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        ordering = ["type"]

    def __str__(self) -> str:
        """Строковое отображение объекта урока"""

        return str(self.name)
