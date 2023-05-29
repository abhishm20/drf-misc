import time
from datetime import datetime


def unix_to_timestamp(uts):
    _ts = int(uts)
    return datetime.utcfromtimestamp(_ts)


def sod(epoch_time):
    timestamp = unix_to_timestamp(epoch_time)
    date = str(timestamp.date()) + " " + "00:00:00"
    return int(time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S")))


def eod(epoch_time):
    timestamp = unix_to_timestamp(epoch_time)
    date = str(timestamp.date()) + " " + "23:59:59"
    return int(time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S")))
