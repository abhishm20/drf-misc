# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django_extra.core.api_exceptions import BadRequest
from django_extra.utility import date_util
from django_extra.utility.date_util import now


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
    match = re.match(
        r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", value
    )
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
    if re.match(
        r"^[0-9]{2}[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}\d[A-Za-z]{1}[A-Za-z0-9]{1}$", value
    ):
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


def validate_business_name(value):
    if not value:
        return True
    if len(value) >= 4:
        return True
    raise BadRequest({"message": "Invalid Business Name."})


def validate_website(value):
    if not value:
        return True
    msg = f"{value} is not valid Website link"
    validate = URLValidator(message=msg)
    return validate(value)


def validate_applicant_dob(value):
    if not value:
        return True
    current_time = date_util.now()
    diff = current_time.date() - value
    year_diff = diff.days / 365.0
    if year_diff > 65:
        raise BadRequest({"message": "Age shouldn't be more than 65 years"})
    if year_diff < 21:
        raise BadRequest({"message": "Age shouldn't be less than 21 years"})
    return True


def validate_incorporation_date(value):
    if not value:
        return True
    current_time = date_util.now()
    diff = value - current_time.date()
    if diff.days > 0:
        raise BadRequest({"message": "Invalid Incorporation Date"})
    return True


def validate_incorporation_year(value):
    if not value:
        return True
    current_time = date_util.now()
    if float(value) > float(date_util.format_time_to(current_time, "%Y")):
        raise BadRequest({"message": "Invalid Incorporation Year"})
    return True


def validate_ifsc(value):
    if not value:
        return True
    if len(value) != 11:
        raise BadRequest({"message": "Invalid ISFC"})
    return True


def validate_decimal_to_int(value):
    try:
        return round(float(value), 0)
    except Exception as ex:
        raise BadRequest({"message": ex}) from ex
    return True


def validate_2_decimal(value):
    try:
        return round(float(value), 2)
    except Exception as exe:
        raise BadRequest({"message": exe}) from exe
    return True


def validate_file_size(value, size):
    if value.size > size:
        raise BadRequest({"message": "File too large. Size should not exceed 10 MB."})
    return True


def validate_person_dob(value, primary):
    if not value:
        return True
    current_time = date_util.now().date()
    diff = (current_time - value).days
    error = {}
    if primary:
        if diff < 18 * 366:
            error = "Age should be more than 18 years"
        if diff > 75 * 366:
            error = "Age should be less than 75 years"
    else:
        if diff < 18 * 366:
            error = "Age should be more than 18 years"
        if diff > 75 * 366:
            error = "Age should be less than 75 years"
    if error:
        raise BadRequest({"message": error})
    return True


def validate_lat_long(lat, long):
    if 90 >= float(lat) >= -90 and float(lat) and 180 >= float(long) >= -180:
        return "Valid"
    raise BadRequest({"message": "Image Latitude and Longitude is Invalid"})


def validate_latitude(value):
    if 90 >= float(value) >= -90 and float(value):
        return True
    raise BadRequest({"message": "Invalid Latitude."})


def validate_longitude(value):
    if 180 >= float(value) >= -180:
        return True
    raise BadRequest({"message": "Longitude is not valid."})


def validate_name_without_special_character(value):
    if re.findall(r"[^A-Za-z0-9\s]", value):
        raise BadRequest({"message": "Special Symbols not Allowed."})
    return True


def validate_dob(value):
    current_time = now()
    diff = current_time.date() - value
    year_diff = diff.days / 365.0
    if year_diff > 100:
        raise BadRequest({"message": "Age shouldn't be more than 100 years"})
    if year_diff < 18:
        raise BadRequest({"message": "Age shouldn't be less than 18 years"})


def validate_image_and_pdf_file():
    # Todo complete this # pylint: disable=fixme
    return True
