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


class EpochField(models.CharField):  # Store as CharField for simplicity
    default_validators = [validate_epoch]

    def __init__(self, *args, **kwargs):
        self.nullable = kwargs.pop("nullable", False)
        self.default_current_time = kwargs.pop("default_current_time", False)
        self.update_now = kwargs.pop("update_now", False)
        kwargs["max_length"] = kwargs.pop("max_length", 20)
        if self.default_current_time:
            kwargs["default"] = str(time.time())
        if self.nullable:
            kwargs["null"] = True
            kwargs["blank"] = True
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if self.update_now:
            value = str(time.time())
            setattr(model_instance, self.attname, value)
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return float(value)

    def to_python(self, value):
        if isinstance(value, float):
            return value
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise ValidationError(
                f"{value} can not be converted to Unix timestamp",
                params={"value": value},
            ) from error

    def get_prep_value(self, value):
        return str(value) if value is not None else value
