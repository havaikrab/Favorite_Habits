from django.contrib import admin

from .models import Habit, Schedule


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Класс представления модели привычки в админ-панели Django"""

    list_display = ("owner", "place", "action", "is_pleasant", "related_habit", "reward", "time_needed", "is_public")
    search_fields = ("owner", "action")
    list_filter = ("is_pleasant", "is_public")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Класс представления модели расписания в админ-панели Django"""

    list_display = ("name", "habit", "type", "constant_interval", "times_in_week", "times_in_month")
    search_fields = ("name", "habit")
    list_filter = ("type",)
