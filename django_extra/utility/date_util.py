# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import date, datetime, timedelta

from django.utils import timezone


def now(datetime_str=None):
    if datetime_str and len(datetime_str) == 10:
        timestamp = datetime.strptime(datetime_str[:10], "%Y-%m-%d")
    elif datetime_str:
        timestamp = datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
    else:
        timestamp = timezone.now()
    return timestamp


def append_current_time(date_part):
    if isinstance(date_part, str):
        date_part = now(date_part)
    time_part = now()
    complete_part = datetime(
        date_part.year,
        date_part.month,
        date_part.day,
        time_part.hour,
        time_part.minute,
        time_part.second,
        time_part.microsecond,
    )
    return complete_part


def delta_time(_tm, ch_dict):
    if _tm is None:
        _tm = now()
    return _tm + timedelta(**ch_dict)


def start_of_day(_dt=None):
    if _dt is None:
        _dt = now()
    return _dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(_dt=None):
    if _dt is None:
        _dt = now()
    return _dt.replace(hour=23, minute=59, second=59, microsecond=999)


def start_of_week(_dt=None):
    if _dt is None:
        _dt = now()
    return start_of_day(_dt) - timedelta(days=_dt.weekday())


def end_of_week(_dt=None):
    if _dt is None:
        _dt = now()
    return end_of_day(delta_time(start_of_week(_dt), {"days": 6}))


def start_of_fortnight(_dt=None):
    if _dt is None:
        _dt = now()
    if _dt.day > 15:
        return delta_time(start_of_month(), {"days": 15})
    return start_of_month()


def end_of_fortnight(_dt=None):
    if _dt is None:
        _dt = now()
    elif _dt.day > 15:
        return end_of_month()
    return end_of_day(
        delta_time(delta_time(start_of_month(), {"days": 15}), {"seconds": -1})
    )


def start_of_month(_dt=None):
    if _dt is None:
        _dt = now()
    return start_of_day(_dt).replace(day=1)


def end_of_month(_dt=None):
    if _dt is None:
        _dt = now()
    return delta_time(
        start_of_month(delta_time(start_of_month(_dt), {"days": 32})), {"seconds": -1}
    )


def add_time(secs, _tm=None):
    if not _tm:
        _tm = now()
    return _tm + timedelta(seconds=secs)


def format_date(date_time):
    if isinstance(date_time, str):
        date_time = datetime.strptime(date_time[:10], "%Y-%m-%d")
    return date_time.strftime("%a, %d %b %Y")


def format_date_time(_dt):
    if isinstance(_dt, str):
        _dt = now(_dt)
    return _dt.strftime("%I:%M %p  %d %b %Y")


def format_time_to(_dt, format_str):
    if isinstance(_dt, str):
        _dt = now(_dt)
    return _dt.strftime(format_str)


def parse_time(formatted_date, format_str):
    return datetime.strptime(formatted_date, format_str)


def get_date_array(start, end, asc=True, period="days"):
    if period == "months":
        days = 30
        factor = "days"
    else:
        days = 1
        factor = period
    if end < start:
        start, end = end, start

    date_iter = [start]
    while (end - start).days > 0:
        start = delta_time(start, {factor: days})
        date_iter.append(start)
    if not asc:
        date_iter = sorted(date_iter, reverse=True)
    return date_iter


def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


def unix_to_timestamp(uts):
    _ts = int(uts)
    return datetime.utcfromtimestamp(_ts)


def sort_days():
    days_name = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    days_index = {name: val for val, name in enumerate(days_name)}
    return days_index
