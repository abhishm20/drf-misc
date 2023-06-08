# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import time
import uuid

from django.db import models

# pylint: disable=no-member,access-member-before-definition,invalid-name


class _DateTimeStampingModel(models.Model):
    created_at = models.CharField(max_length=32, null=True, default=None)
    updated_at = models.CharField(max_length=32, null=True, default=None)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
            self.created_at = int(time.time())
        self.updated_at = int(time.time())
        super().save(*args, **kwargs)


class AllInstanceManager(models.Manager):
    def get_queryset(self):
        return super(AllInstanceManager, self).get_queryset().filter()


class OnlyActiveInstanceManager(models.Manager):
    def get_queryset(self):
        return (
            super(OnlyActiveInstanceManager, self)
            .get_queryset()
            .filter(is_deleted=False)
        )


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
    id = models.CharField(editable=False, unique=True, primary_key=True, max_length=36)

    class Meta:
        abstract = True