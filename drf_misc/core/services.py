# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from drf_misc.core.api_exceptions import BadRequest  # pylint: disable=import-error

# pylint: disable=not-callable
from drf_misc.core.cache import CustomCache
from drf_misc.settings import app_settings


class BaseService:
    serializer = None
    cache_enabled = False
    cache_serializer = None
    model = None
    update_fields = []

    def __init__(self, instance_id=None, instance=None):
        if instance_id:
            self.instance = get_object_or_404(self.model, id=instance_id)
        elif instance:
            self.instance = instance

    def get_cache_key(self):
        return f"{app_settings.service_name}:{self.instance.__class__.__name__.lower()}:{self.instance.id}"

    def create(self, data):
        ser = self.serializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        self.set_cache()
        return self.instance

    def delete(self):
        if app_settings.use_service_cache and self.cache_enabled:
            CustomCache(self.get_cache_key()).delete()
        self.instance.delete()

    def update(self, data, partial=True):
        if self.update_fields:
            data = {key: value for key, value in data.items() if key in self.update_fields}

        ser = self.serializer(self.instance, data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance

        self.set_cache()
        return self.instance

    def force_update(self, data, partial=True):
        ser = self.serializer(self.instance, data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance

        self.set_cache()
        return self.instance

    def set_cache(self, data=None, raise_exception=False):
        if app_settings.use_service_cache and self.cache_enabled:
            if not data:
                serializer = self.cache_serializer or self.serializer
                data = serializer(self.instance).data
            CustomCache(self.get_cache_key()).set(data)
        elif raise_exception:
            raise BadRequest({"message": f"Caching is not configured for {self.model.__class__.__name__}"})
