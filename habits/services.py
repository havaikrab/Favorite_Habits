from datetime import datetime, timedelta


def get_next_with_constant_interval(start_at: str, interval: int) -> int:
    """Определяет метку времени наступления следующего события для "constant_interval"-расписания"""

    now = datetime.now().timestamp()
    start_stamp = datetime.fromisoformat(start_at).timestamp()
    if start_stamp < now:
        start_stamp += ((now - start_stamp) / 60 // interval + 1) * 60 * interval
    return int(start_stamp)


def get_next_with_times_in_week(start_at: str, times_in_week: list[int]) -> int:
    """Определяет метку времени наступления следующего события для "times_in_week"-расписания"""

    now = datetime.now().timestamp()
    start_obj = datetime.fromisoformat(start_at)
    monday = start_obj - timedelta(days=start_obj.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    start_stamp = monday.timestamp()
    if now - start_stamp > 60 * 60 * 24 * 7:
        start_stamp += ((now - start_stamp) // (60 * 60 * 24 * 7)) * 60 * 60 * 24 * 7
    for minute in sorted(times_in_week):
        if start_stamp + minute * 60 > now:
            return int(start_stamp + minute * 60)
    return int(60 * 60 * 24 * 7 + start_stamp + min(times_in_week) * 60)


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
