# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404  # pylint: disable=import-error

# pylint: disable=not-callable
from drf_misc.core.audit_service import AuditService
from drf_misc.core.cache import CustomCache
from drf_misc.settings import app_settings
from drf_misc.utility.misc import diff_dict


class BaseService:
    serializer = None
    cache_serializer = None
    model = None
    audit_enable = None
    get_entity_data = None
    update_fields = []

    def __init__(self, instance_id=None, instance=None):
        if instance_id:
            self.instance = get_object_or_404(self.model, id=instance_id)
        elif instance:
            self.instance = instance

    def get_cache_key(self):
        return f"{app_settings.service_name}:\
                {self.instance.__class__.__name__.lower()}:{self.instance.id}"

    def create(self, data, request, audit_data=None):
        ser = self.serializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).set(
                self.cache_serializer(self.instance).data
            )

        if self.audit_enable:
            entity = self.get_entity_data()
            audit_data = self._get_audit_data("created", audit_data)
            AuditService().send_event(entity, data, request, audit_data)
        return self.instance

    def delete(self, request, audit_data=None):
        audit_data = self._get_audit_data("deleted", audit_data)
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).delete()
        if self.audit_enable:
            entity = self.get_entity_data()
            AuditService().send_event(
                entity, self.serializer(self.instance).data, request, audit_data
            )
        self.instance.delete()

    def update(self, data, request, audit_data=None, partial=True):
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
        if self.audit_enable:
            entity = self.get_entity_data()
            audit_data = self._get_audit_data("updated", audit_data)
            AuditService().send_event(entity, diff_data, request, audit_data)
        return self.instance

    def force_update(self, data, request, audit_data=None, partial=True):
        diff_data = diff_dict(self.serializer(self.instance).data, data)
        ser = self.serializer(self.instance, data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        self.instance = ser.instance
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).set(
                self.cache_serializer(self.instance).data
            )
        if self.audit_enable:
            entity = self.get_entity_data()
            audit_data = self._get_audit_data("updated", audit_data)
            AuditService().send_event(entity, diff_data, request, audit_data)
        return self.instance

    def _get_audit_data(self, action, audit_data=None):
        if not audit_data:
            audit_data = {}
        if not audit_data.get("action"):
            audit_data["action"] = action
        if not audit_data.get("remark"):
            audit_data["remark"] = f"{self.model.__class__.__name__} {action}"
        if not audit_data.get("level"):
            audit_data["level"] = "info"
        return audit_data