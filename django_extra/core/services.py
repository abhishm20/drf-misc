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
        return f"{app_settings.service_name}:{self.instance.__class__.__name__.lower()}:{self.instance.id}"
    
    def create(self, data, action="created", request=dict, level="trace", remark=""):
        with transaction.atomic():
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
                AuditService().send_event(
                    action,
                    entity,
                    data,
                    request,
                    level=level,
                    remark=remark
                )
            return self.instance
    
    def delete(self, action="deleted", request=dict, level="trace", remark=""):
        if app_settings.use_service_cache and self.cache_serializer:
            CustomCache(self.get_cache_key()).delete()
        if self.audit_enable and request:
            entity = self.get_entity_data()
            AuditService().send_event(
                action,
                entity,
                self.serializer(self.instance).data,
                request,
                level=level,
                remark=remark)
        self.instance.delete()
    
    def update(self, data, action="updated", request=dict, partial=True, level="trace", remark=""):
        with transaction.atomic():
            ser = self.serializer(self.instance, data, partial=partial)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.use_service_cache and self.cache_serializer:
                CustomCache(self.get_cache_key()).set(self.cache_serializer(self.instance).data)
            if self.audit_enable and request:
                entity = self.get_entity_data()
                AuditService().send_event(
                    action,
                    entity,
                    data,
                    request,
                    level=level,
                    remark=remark
                )
            return self.instance
