# -*- coding: utf-8 -*-

from django.core.cache import cache


class CustomCache:
    def __init__(self, key=None):
        self.key = key

    def get(self):
        value = cache.get(self.key)
        return value

    def delete(self):
        cache.delete(self.key)

    def set(self, value):
        value = cache.set(self.key, value)
        return value
