# -*- coding: utf-8 -*-

from django.core.cache import cache

from django_extra.core.api_exceptions import ServerError
from django_extra.settings import app_settings


class CustomCache:
    def __init__(self, key=None, model=None, _pk=None, instance=None, duration=60):
        if key:
            self.key = key
        elif instance:
            self.key = self.get_cache_key(instance)
        elif model and _pk:
            self.key = self.get_cache_key_by_model_name_and_id(model, _pk)
        else:
            raise ServerError({"message": "Cache key is required"})
        self.duration = duration

    def get(self):
        value = cache.get(self.key)
        return value

    def delete(self):
        cache.delete(self.key)

    def set(self, value):
        value = cache.set(self.key, value, self.duration)
        return value

    @staticmethod
    def get_cache_key(instance):
        key = f"{app_settings.SERVICE_NAME}-{instance.__class__.__name__}-{instance.id}"
        return key

    @staticmethod
    def get_cache_key_by_model_name_and_id(model, _pk):
        key = f"{app_settings.SERVICE_NAME}-{model}-{_pk}"
        return key
