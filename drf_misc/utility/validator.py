# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from drf_misc.core.api_exceptions import BadRequest


def validate_mobile(value, raise_exception=True, mobile_no_only=True):
    if not value:
        raise BadRequest({"message": "Invalid Mobile."})
    if mobile_no_only:
        match = re.match(r"[6789]\d{9}$", value)
    else:
        match = re.match(r"^\d{5,15}$", value)
    if not match:
        if raise_exception:
            raise BadRequest({"message": "Invalid Mobile."})
        return False
    return True


def validate_email(value, raise_exception=True):
    if not value:
        return True
    match = re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", value)
    if not match:
        if raise_exception:
            raise BadRequest({"message": "Invalid Email."})
        return False
    return True


def validate_url(value):
    if not value:
        return True
    msg = f"{value} is not valid Website link"
    validate = URLValidator(message=msg)
    try:
        validate(value)
        return True
    except ValidationError:
        return False


def validate_pan(value):
    if not value:
        return True
    if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", value):
        return True
    raise BadRequest({"message": "Invalid PAN."})


def validate_gst(value):
    if not value:
        return True
    if re.match(r"^[0-9]{2}[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}\d[A-Za-z]{1}[A-Za-z0-9]{1}$", value):
        return True
    raise BadRequest({"message": "Invalid GST."})


def validate_aadhaar(value):
    if not value:
        return True
    if len(value) == 12 and re.match(r"^[0-9]{12}", value):
        return True
    raise BadRequest({"message": "Invalid Aadhaar."})


def validate_pincode(value):
    if not value:
        return True
    if len(value) == 6 and re.match(r"^[0-9]{6}", value):
        return True
    raise BadRequest({"message": "Invalid Pincode."})


def validate_website(value):
    if not value:
        return True
    msg = f"{value} is not valid Website link"
    validate = URLValidator(message=msg)
    return validate(value)


def validate_ifsc(value):
    if not value:
        return True
    if len(value) != 11:
        raise BadRequest({"message": "Invalid ISFC"})
    return True
