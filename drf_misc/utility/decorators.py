# -*- coding: utf-8 -*-
import time
from re import DEBUG

from django.db import connection, reset_queries


def query_debugger(func):
    def inner_func(*args, **kwargs):
        if DEBUG:
            reset_queries()
            st = time.time()
        result = func(*args, **kwargs)

        if DEBUG:
            print(
                f"------Queries count for {func.__qualname__}: {len(connection.queries)}------"
            )
            print(f"------Time taken for {func.__qualname__}: {time.time() - st}------")
        return result

    return inner_func
