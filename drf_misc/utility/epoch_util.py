# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta


def unix_to_dt(unix):
    # uts can be 1686868399 or 1686868399000 or 1686868399.000
    if len(str(unix)) > 11 and "." not in str(unix):
        unix = float(unix) / 1000
    else:
        unix = float(unix)
    return datetime.fromtimestamp(unix)


def dt_to_unix(date_time):
    # dt can be date instance or datetime instance
    if isinstance(date_time, str):
        if len(date_time) == 10:
            date_time = datetime.strptime(date_time[:10], "%Y-%m-%d")
        elif len(date_time) > 10 and "T" in date_time:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
        else:
            date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    if len(str(date_time)) <= 10:
        date_time = datetime(date_time.year, date_time.month, date_time.day)
    return int(time.mktime(date_time.timetuple()))


def append_current_time(unix):
    date_part = unix_to_dt(unix)
    time_part = datetime.now()
    complete_part = datetime(
        date_part.year,
        date_part.month,
        date_part.day,
        time_part.hour,
        time_part.minute,
        time_part.second,
        time_part.microsecond,
    )
    return dt_to_unix(complete_part)


def sod(unix):
    return dt_to_unix(
        unix_to_dt(unix).replace(hour=0, minute=0, second=0, microsecond=0)
    )


def eod(unix):
    return dt_to_unix(
        unix_to_dt(unix).replace(hour=23, minute=59, second=59, microsecond=999999)
    )


def delta_time(unix, ch_dict):
    date_time = unix_to_dt(unix)
    return dt_to_unix(date_time + timedelta(**ch_dict))


def get_date_array(start, count, asc=True, period="days"):
    date_iter = []
    temp = sod(start)
    for _ in range(count):
        date_iter.append((temp, eod(temp)))
        if asc:
            temp = delta_time(temp, {period: 1})
        else:
            temp = delta_time(temp, {period: -1})

    return date_iter
