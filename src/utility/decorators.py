# -*- coding: utf-8 -*-
import functools
import time

from django.db import connection, reset_queries


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        len(connection.queries)

        time.perf_counter()
        result = func(*args, **kwargs)
        time.perf_counter()

        len(connection.queries)
        return result

    return inner_func
