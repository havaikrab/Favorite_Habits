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
    minutes_list.sort()
    if minutes_list[0] > 5760:
        raise ValidationError("Минимальное значение в списке times_in_month не может быть больше 5760")
    last_steady_value = None
    for j in range(len(minutes_list) - 1):
        if minutes_list[j + 1] - minutes_list[j] > 10080:
            raise ValidationError(f"Разница между {minutes_list[j]} и {minutes_list[j + 1]} превышает значение 10080")
        if minutes_list[j + 1] > 40320 and last_steady_value is None:
            last_steady_value = minutes_list[j]
    if last_steady_value is None:
        last_steady_value = minutes_list[-1]
    if 34560 + minutes_list[0] > last_steady_value:
        raise ValidationError(f"""При наименьшем значении {minutes_list[0]} в списке times_in_month также обязательно
        должно быть указано значение, удовлетворяющее условию {34560 + minutes_list[0]} <= required_value <= 40320""")
    return minutes_list
