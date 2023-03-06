# -*- coding: utf-8 -*-

from django.core.cache import cache


class CustomCache:
    def __init__(self, key=None, duration=60):
        self.key = key
        self.duration = duration

    def get(self):
        value = cache.get(self.key)
        return value

    def delete(self):
        cache.delete(self.key)

    def set(self, value):
        value = cache.set(self.key, value, self.duration)
        return value
