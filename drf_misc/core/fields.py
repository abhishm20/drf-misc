# -*- coding: utf-8 -*-
import time
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models


def validate_epoch(value):
    try:
        datetime.utcfromtimestamp(float(value))
    except (ValueError, TypeError) as error:
        raise ValidationError(
            f"{value} is not a valid Unix timestamp",
            params={"value": value},
        ) from error


class EpochField(models.FloatField):  # Store as CharField for simplicity
    default_validators = [validate_epoch]

    def __init__(self, *args, **kwargs):
        self.nullable = kwargs.pop("nullable", True)
        self.default_current_time = kwargs.pop("default_current_time", False)
        self.update_now = kwargs.pop("update_now", False)
        kwargs["max_length"] = kwargs.pop("max_length", 20)
        if self.default_current_time:
            kwargs["default"] = time.time
        if self.nullable:
            kwargs["null"] = True
            kwargs["blank"] = True
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if self.update_now:
            value = float(time.time())
            setattr(model_instance, self.attname, value)
        return value

    def from_db_value(self, value, expression, connection):
        if not value:
            return None
        return float(value)

    def to_python(self, value):
        if value:
            float(value)
        return None

    def get_prep_value(self, value):
        return float(value) if value is not None else value
