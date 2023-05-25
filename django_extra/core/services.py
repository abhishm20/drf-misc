# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

# pylint: disable=not-callable
from django_extra.core.audit_service import AuditService
from django_extra.core.cache import CustomCache
from django_extra.settings import app_settings
from django_extra.utility.misc import diff_dict


class BaseService:
    serializer = None
    cache_serializer = None
    model = None
    audit_enable = None
    get_entity_data = None
    update_fields = []

    def __init__(self, instance_id=None):
        if instance_id:
            self.instance = get_object_or_404(self.model, id=instance_id)

    def get_cache_key(self):
        return f"{app_settings.service_name}:{self.instance.__class__.__name__.lower()}:{self.instance.id}"

    def create(self, data, request=None, audit_data=None):
        if not audit_data:
            audit_data = {
                "action": "created",
                "remark": f"{self.model.__class__.__name__} created",
                "level": "info",
            }
        ser = self.serializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).set(
                self.cache_serializer(self.instance).data
            )

        if self.audit_enable and request:
            entity = self.get_entity_data()
            AuditService().send_event(entity, data, request, audit_data)
        return self.instance

    def delete(self, request=None, audit_data=None):
        if not audit_data:
            audit_data = {
                "action": "deleted",
                "remark": f"{self.model.__class__.__name__} deleted",
                "level": "info",
            }
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).delete()
        if self.audit_enable and request:
            entity = self.get_entity_data()
            AuditService().send_event(
                entity, self.serializer(self.instance).data, request, audit_data
            )
        self.instance.delete()

    def update(self, data, partial=True, request=None, audit_data=None):
        if not audit_data:
            audit_data = {
                "action": "updated",
                "remark": f"{self.model.__class__.__name__} updated",
                "level": "info",
            }
        if self.update_fields:
            data = {
                key: value for key, value in data.items() if key in self.update_fields
            }
        diff_data = diff_dict(self.serializer(self.instance).data, data)
        ser = self.serializer(self.instance, data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).set(
                self.cache_serializer(self.instance).data
            )
        if self.audit_enable and request:
            entity = self.get_entity_data()
            AuditService().send_event(entity, diff_data, request, audit_data)
        return self.instance

    def force_update(self, data, partial=True, request=None, audit_data=None):
        if not audit_data:
            audit_data = {
                "action": "updated",
                "remark": f"{self.model.__class__.__name__} updated",
                "level": "info",
            }
        diff_data = diff_dict(self.serializer(self.instance).data, data)
        ser = self.serializer(self.instance, data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).set(
                self.cache_serializer(self.instance).data
            )
        if self.audit_enable and request:
            entity = self.get_entity_data()
            AuditService().send_event(entity, diff_data, request, audit_data)
        return self.instance
