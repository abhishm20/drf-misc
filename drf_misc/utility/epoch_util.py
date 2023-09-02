# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta


def unix_to_dt(unix):
    # uts can be 1686868399 or 1686868399000 (millisecond) or 1686868399.000 or 1686868399000000 (microseconds) [Not supported for now]
    if len(str(unix)) > 11 and "." not in str(unix):
        unix = float(unix) / 1000
    else:
        unix = float(unix)
    return datetime.fromtimestamp(unix)


def get_days_diff(start_date, end_date, zero_as_min=True):
    days = (unix_to_dt(end_date).date() - unix_to_dt(start_date).date()).days
    if zero_as_min:
        return max(days, 0)
    return days


def dt_to_unix(date_time):
    # dt can be date instance or datetime instance
    if isinstance(date_time, str):
        if len(date_time) == 10:
            date_time = datetime.strptime(date_time[:10], "%Y-%m-%d")
        elif len(date_time) > 10 and "." in date_time:
            if "T" in date_time:
                date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S.%f")
        elif len(date_time) > 10 and "." not in date_time:
            if "T" in date_time:
                date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
            else:
                date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    return float(date_time.timestamp())


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
    return dt_to_unix(unix_to_dt(unix).replace(hour=0, minute=0, second=0, microsecond=0))


def eod(unix):
    return dt_to_unix(unix_to_dt(unix).replace(hour=23, minute=59, second=59, microsecond=999999))


def delta_time(unix, ch_dict):
    date_time = unix_to_dt(unix)
    return dt_to_unix(date_time + relativedelta(**ch_dict))


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
