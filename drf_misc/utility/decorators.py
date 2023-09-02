# -*- coding: utf-8 -*-
import time
from re import DEBUG

from django.db import connection, reset_queries

from drf_misc.settings import app_settings


def query_debugger(func):
    def inner_func(*args, **kwargs):
        if DEBUG:
            reset_queries()
            start_time = time.time()
        result = func(*args, **kwargs)

        if DEBUG and app_settings.app_logger:
            app_settings.app_logger(f"------Queries count for {func.__qualname__}: {len(connection.queries)}------")
            app_settings.app_logger(f"------Time taken for {func.__qualname__}: {time.time() - start_time}------")
        return result

    return inner_func
