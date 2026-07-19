import logging
from datetime import datetime, timedelta

from habits.models import Habit, Schedule

logger = logging.getLogger(__name__)


def get_next_with_constant_interval(start_at: str, interval: int) -> int:
    """Определяет метку времени наступления следующего события для "constant_interval"-расписания"""

    now = datetime.now().timestamp()
    start_stamp = datetime.fromisoformat(start_at).timestamp()
    if start_stamp < now:
        minutes_delta = now / 60 - start_stamp / 60
        intervals_count = minutes_delta // interval
        intervals_count += 1
        seconds_to_add = intervals_count * 60 * interval
        start_stamp += seconds_to_add
    return int(start_stamp)


def get_next_with_times_in_week(start_at: str, times_in_week: list[int]) -> int:
    """Определяет метку времени наступления следующего события для "times_in_week"-расписания"""

    now = datetime.now().timestamp()
    start_obj = datetime.fromisoformat(start_at)
    monday = start_obj - timedelta(days=start_obj.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    start_stamp = monday.timestamp()
    seconds_delta = now - start_stamp
    if seconds_delta > 604800:
        intervals_count = seconds_delta // 604800
        seconds_to_add = intervals_count * 604800
        start_stamp += seconds_to_add
    for minute in sorted(times_in_week):
        if start_stamp + minute * 60 > now:
            return int(start_stamp + minute * 60)
    return int(min(times_in_week) * 60 + start_stamp + 604800)


def get_next_with_times_in_month(start_at: str, times_in_month: list[int]) -> int:
    """Определяет метку времени наступления следующего события для "times_in_month"-расписания"""

    start_obj = datetime.fromisoformat(start_at)
    base_stamp = start_obj.timestamp()
    now_obj = datetime.now(tz=start_obj.tzinfo)
    if start_obj < now_obj:
        start_month = now_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_month = start_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_month_stamp = start_month.timestamp()
    if start_month.month == 2:
        if start_month.year % 4 == 0:
            days = 29
        else:
            days = 28
    elif start_month.month in [4, 6, 9, 11]:
        days = 30
    else:
        days = 31
    end_month_stamp = days * 24 * 60 * 60 + start_month_stamp
    now_stamp = now_obj.timestamp()
    for minute in sorted(times_in_month):
        if max(base_stamp, now_stamp) < start_month_stamp + minute * 60 < end_month_stamp:
            return int(start_month_stamp + minute * 60)
    return int(end_month_stamp + min(times_in_month) * 60)


def set_next_event(schedule: Schedule) -> Schedule:
    """Обновляет значение поля next_event у объектов модели Schedule !!!без сохранения в базе данных!!!"""

    if schedule.type == "constant_interval":
        next_event = get_next_with_constant_interval(schedule.start_at, schedule.constant_interval)
    elif schedule.type == "times_in_week":
        next_event = get_next_with_times_in_week(schedule.start_at, schedule.times_in_week)
    elif schedule.type == "times_in_month":
        next_event = get_next_with_times_in_month(schedule.start_at, schedule.times_in_month)
    else:
        logger.critical("Schedule pk=%d: содержит недопустимое значение поля type", schedule.pk)
        raise ValueError("Некорректное значение в базе данных")
    schedule.next_event = next_event
    return schedule


def create_message(habit: Habit) -> str:
    """Формирует текст сообщения для отправки пользователю в telegram-чат"""

    if habit.is_pleasant:
        message = f'Время порадовать себя! Отправься в "{habit.place}" и сделай "{habit.action}"!'
    else:
        message = f'Пора отправиться в "{habit.place}" и сделать "{habit.action}"!'
        if habit.reward:
            message += f' Не забудь про награду "{habit.reward}"!'
        else:
            related = habit.related_habit
            if hasattr(related, "schedule"):
                print("Есть расписание")
                message += f' Я напомню тебе, когда придет время для "{related.action}".'
            else:
                message += f' Не забудь порадовать себя, сделав "{related.action}".'
    return message


def prepare_events() -> None:
    """Извлекает из базы данных объекты расписания,
    связанные привычки которых должны быть выполнены в ближайшую минуту"""

    lower_stamp = datetime.now().timestamp()
    upper_stamp = lower_stamp + 60
    queryset = Schedule.objects.filter(next_event__lt=upper_stamp).select_related(
        "habit__owner", "habit__related_habit"
    )
    to_execute = queryset.filter(next_event__gte=lower_stamp)
    expired = queryset.difference(to_execute)
    for schedule in to_execute:
        chat_id = schedule.habit.owner.tg_chat_id
        if chat_id:
            message = create_message(schedule.habit)
            result = {schedule.next_event: {chat_id: message}}  # Положить в кеш с ключом schedule.next_event
    to_update = list()
    for schedule in expired:
        expired_date = datetime.isoformat(datetime.fromtimestamp(schedule.next_event))
        schedule = set_next_event(schedule)
        next_date = datetime.isoformat(datetime.fromtimestamp(schedule.next_event))
        logger.warning(
            "Schedule pk=%d: пропущено событие %s, следующее событие %s", schedule.pk, expired_date, next_date
        )
        to_update.append(schedule)
    Schedule.objects.bulk_update(to_update, ["next_event"])
