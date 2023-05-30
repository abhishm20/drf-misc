import time
from datetime import datetime
import moment


def unix_to_timestamp(uts):
    _ts = int(uts)
    return datetime.utcfromtimestamp(_ts)


def sod(epoch_time):
    return (
        moment.unix(epoch_time).replace(hours=23, minutes=59, seconds=59).zero.epoch()
    )


def eod(epoch_time):
    return moment.unix(epoch_time).replace(hours=23, minutes=59, seconds=59).epoch()


def delta_time(_tm, days):
    if _tm is None:
        _tm = int(time.time())
    return moment.unix(int(_tm)).add(days=day)


def get_date_array(start, count, asc=True, period="days"):
    date_iter = []
    temp = moment.unix(start)
    for _ in range(count):
        date_iter.append((temp.zero.epoch(), eod(temp.epoch())))
        if asc:
            temp = temp.add(**{period: 1})
        else:
            temp = temp.subtract(**{period: 1})
    for a in date_iter:
        print(
            moment.unix(a[0]).timezone("Asia/Kolkata"),
            moment.unix(a[1]).timezone("Asia/Kolkata"),
        )
    return date_iter
