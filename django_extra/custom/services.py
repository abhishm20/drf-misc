# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import transaction

from django_extra.custom.cache import CustomCache
from django_extra.settings import app_settings

# pylint: disable=not-callable


class BaseService:
    serializer = None
    model = None

    def __init__(self, instance=None):
        self.instance = instance

    def create(self, data):
        with transaction.atomic():
            ser = self.serializer(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.USE_SERVICE_CACHE:
                CustomCache(instance=self.instance).set(ser.data)
            return self.instance

    def delete(self):
        if app_settings.USE_SERVICE_CACHE:
            CustomCache(instance=self.instance).delete()
        self.instance.delete()

    def update(self, data, partial=True):
        with transaction.atomic():
            ser = self.serializer(self.instance, data, partial=partial)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.USE_SERVICE_CACHE:
                CustomCache(instance=self.instance).set(ser.data)
            return self.instance
