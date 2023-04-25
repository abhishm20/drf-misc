# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import transaction
from django.shortcuts import get_object_or_404
from django_extra.core.cache import CustomCache
from django_extra.settings import app_settings
# pylint: disable=not-callable
from django_extra.core.aws_api import AWSApi


class BaseService:
    serializer = None
    cache_serializer = None
    model = None
    audit_enable = None
    
    def __init__(self, instance_id=None):
        if instance_id:
            self.instance = get_object_or_404(self.model, id=instance_id)
    
    def get_cache_key(self):
        return f"{app_settings.SERVICE_NAME}:{self.instance.__class__.__name__.lower()}:{self.instance.id}"
    
    def create(self, data, request=dict):
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
                sqs = AWSApi("sqs")
                sqs.send_message(
                    self.instance,
                    data=data,
                    request=request,
                    remark=f"create {self.instance.__class__.__name__}",
                    action="create")
            return self.instance
    
    def delete(self, request=dict):
        if app_settings.USE_SERVICE_CACHE and self.cache_serializer:
            CustomCache(self.get_cache_key()).delete()
        self.instance.delete()
        if self.audit_enable:
            sqs = AWSApi("sqs")
            sqs.send_message(
                self.instance,
                data="",
                request=request,
                remark=f"delete {self.instance.__class__.__name__}",
                action="delete")
    
    def update(self, data, request=dict, partial=True):
        with transaction.atomic():
            ser = self.serializer(self.instance, data, partial=partial)
            ser.is_valid(raise_exception=True)
            ser.save()
            self.instance = ser.instance
            if app_settings.USE_SERVICE_CACHE and self.cache_serializer:
                CustomCache(self.get_cache_key()).set(
                    self.cache_serializer(self.instance).data
                )
            if self.audit_enable:
                sqs = AWSApi("sqs")
                sqs.send_message(
                    self.instance,
                    data="",
                    request=request,
                    remark=f"update {self.instance.__class__.__name__}",
                    action="update")
            return self.instance
