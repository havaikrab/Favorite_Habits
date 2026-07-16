from typing import cast

from django.db.models import QuerySet
from django.http import HttpRequest
from django_filters.rest_framework import BooleanFilter, FilterSet

from habits.models import Habit


class HabitFilterSet(FilterSet):
    """Набор фильтров для модели привычки"""

    owner = BooleanFilter(method="owner_filter", label="Признак собственности")
    public = BooleanFilter(method="public_filter", label="Признак публичности")
    pleasant = BooleanFilter(method="pleasant_filter", label="Признак приятной привычки")

    class Meta:
        """Параметры фильтр-сэта"""

        model = Habit
        fields = {"action": ["icontains"]}

    def owner_filter(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Фильтр-метод параметра owner"""

        self_request = cast(HttpRequest, self.request)
        user = self_request.user
        if value is True:
            return queryset.filter(owner=user)
        elif value is False:
            return queryset.exclude(owner=user)
        return queryset

    def public_filter(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Фильтр-метод параметра public"""

        if value is True:
            return queryset.filter(is_public=True)
        elif value is False:
            return queryset.filter(is_public=False)
        return queryset

    def pleasant_filter(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Фильтр-метод параметра pleasant"""

        if value is True:
            return queryset.filter(is_pleasant=True)
        elif value is False:
            return queryset.filter(is_pleasant=False)
        return queryset
