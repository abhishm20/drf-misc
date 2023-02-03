# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import uuid

from django.db import models

from django_extra import utility

# pylint: disable=no-member


class _DateTimeStampingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = utility.now()
        self.updated_at = utility.now()
        super().save(*args, **kwargs)


class AbstractModel(_DateTimeStampingModel):
    id = models.CharField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True, max_length=50
    )

    class Meta:
        abstract = True
