# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import time
import uuid

from django.db import models

from drf_misc.core.fields import EpochField

# pylint: disable=no-member,access-member-before-definition,invalid-name


class _DateTimeStampingModel(models.Model):
    created_at = EpochField(default_current_time=True)
    updated_at = EpochField(nullable=True, update_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        self.updated_at = str(time.time())
        super().save(*args, **kwargs)


class AllInstanceManager(models.Manager):
    def get_queryset(self):
        return super(AllInstanceManager, self).get_queryset().filter()


class OnlyActiveInstanceManager(models.Manager):
    def get_queryset(self):
        return super(OnlyActiveInstanceManager, self).get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.CharField(null=True, blank=True)

    objects = OnlyActiveInstanceManager()
    all_objects = AllInstanceManager()

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.deleted_at = int(time.time())
        self.save()


class AbstractModel(_DateTimeStampingModel):
    id = models.CharField(editable=False, unique=True, primary_key=True, max_length=50)

    class Meta:
        abstract = True
