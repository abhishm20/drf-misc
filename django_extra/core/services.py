# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import transaction
from django.shortcuts import get_object_or_404
from django_extra.core.cache import CustomCache
from django_extra.settings import app_settings
# pylint: disable=not-callable
from django_extra.core.audit_service import AuditService


class BaseService:
    serializer = None
    cache_serializer = None
    model = None
    audit_enable = None
    get_entity_data = None
    
    def __init__(self, instance_id=None):
        if instance_id:
            self.instance = get_object_or_404(self.model, id=instance_id)
    
    def get_cache_key(self):
        return f"{app_settings.SERVICE_NAME}:{self.instance.__class__.__name__.lower()}:{self.instance.id}"
    
    def create(self, data, request=dict, is_critical=True):
        with transaction.atomic():
            ser = self.serializer(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.USE_SERVICE_CACHE and self.cache_serializer:
                CustomCache(self.get_cache_key()).set(
                    self.cache_serializer(self.instance).data
                )
            
            if self.audit_enable:
                entity = self.get_entity_data()
                AuditService().send_event(
                    "create",
                    entity,
                    data,
                    request,
                    is_critical=is_critical
                )
            return self.instance
    
    def delete(self, request=dict, is_critical=True):
        if app_settings.USE_SERVICE_CACHE and self.cache_serializer:
            CustomCache(self.get_cache_key()).delete()
        if self.audit_enable:
            entity = self.get_entity_data()
            AuditService().send_event(
                "delete",
                entity,
                self.serializer(self.instance).data,
                request,
                is_critical=is_critical)
        self.instance.delete()
    
    def update(self, data, request=dict, partial=True, is_critical=False):
        with transaction.atomic():
            ser = self.serializer(self.instance, data, partial=partial)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.USE_SERVICE_CACHE and self.cache_serializer:
                CustomCache(self.get_cache_key()).set(self.cache_serializer(self.instance).data)
            if self.audit_enable:
                entity = self.get_entity_data()
                AuditService().send_event(
                    "update",
                    entity,
                    data,
                    request,
                    is_critical=is_critical
                )
            return self.instance
