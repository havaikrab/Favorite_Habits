from rest_framework.exceptions import ValidationError


def validate_month_minutes_list(minutes_list: list) -> list:
    """Принимает список значений "минута в месяце" и проверяет разницу между значениями.
    Также проверяется разница между последним значением в "текущем месяце" и первым значением в "следующем месяце".
    Разница не может превышать значение 10080, соответствующее продолжительности одной недели"""

    if len(minutes_list) != len(set(minutes_list)):
        raise ValidationError("Значения в списке times_in_month не должны повторяться")
    elif len(minutes_list) < 5:
        raise ValidationError("Список times_in_month не может содержать меньше пяти значений")
    for i in minutes_list:
        if not isinstance(i, int) or not 1 <= i <= 44640:
            raise ValidationError("Все значения в списке times_in_month должны быть целыми числами от 1 до 44640")
    sorted_minutes = sorted(minutes_list)
    if sorted_minutes[0] > 5760:
        raise ValidationError("Минимальное значение в списке times_in_month не может быть больше 5760")
    last_steady_value = None
    for j in range(len(sorted_minutes) - 1):
        if sorted_minutes[j + 1] - sorted_minutes[j] > 10080:
            raise ValidationError(
                f"Разница между {sorted_minutes[j]} и {sorted_minutes[j + 1]} превышает значение 10080"
            )
        if sorted_minutes[j + 1] > 40320 and last_steady_value is None:
            last_steady_value = sorted_minutes[j]
    if last_steady_value is None:
        last_steady_value = sorted_minutes[-1]
    if 34560 + sorted_minutes[0] > last_steady_value:
        raise ValidationError(
            f"""При наименьшем значении {sorted_minutes[0]} в списке times_in_month также обязательно
        должно быть указано значение, удовлетворяющее условию {34560 + sorted_minutes[0]} <= required_value <= 40320"""
        )
    return minutes_list
