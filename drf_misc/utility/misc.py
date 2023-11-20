# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import mimetypes
import random
import string
from collections import OrderedDict
from itertools import tee

from unidecode import unidecode  # pylint: disable=import-error

from drf_misc.core.api_exceptions import BadRequest
from drf_misc.settings import app_settings


def generate_password():
    # characters to generate password from
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    random.shuffle(characters)
    # picking random characters from the list
    password = []
    password.append(random.choice(characters))
    # shuffling the resultant password
    random.shuffle(password)
    return "".join(password)


def remove_non_ascii(text):
    return unidecode(str(text, encoding="utf-8"))


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    _a, _b = tee(iterable)
    next(_b, None)
    return zip(_a, _b)


def split_full_name(full_name):
    splitted_name = full_name.split()
    if len(splitted_name) == 3:
        return splitted_name
    if len(splitted_name) == 2:
        return splitted_name[0], "", splitted_name[1]
    if len(splitted_name) == 1:
        return splitted_name[0], "", ""
    return splitted_name[0], splitted_name[1], " ".join(splitted_name[2:])


def get_mime_type(file_path):
    return mimetypes.MimeTypes().guess_type(file_path)[0]


def format_constants(value):
    """
    Converts abc_xyz > Abc Xyz
    :param value:
    :return:
    """
    return " ".join(value.split("_")).title()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        _ip = x_forwarded_for.split(",")[0]
    else:
        _ip = request.META.get("REMOTE_ADDR")
    return _ip


def make_name_value_pair(set_list):
    return [{"name": x[1], "value": x[0]} for x in set_list]


def flatten_object(obj):
    new_obj = {}
    for key in obj.keys():
        if type(obj[key]) in [dict, OrderedDict]:
            _a = flatten_object(obj[key])
            new_obj.update({key + "_" + k: _a[k] for k in _a.items()})
        else:
            new_obj[key] = obj[key]
    return new_obj


def mask_string(s_value, unmasked_length=4):
    if s_value:
        return f"{'*' * (len(s_value) - unmasked_length)}{s_value[:unmasked_length]}"
    return ""


def diff_dict(dict1, dict2):
    diff = {}
    for k in dict1:
        if k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                nested_diff = diff_dict(dict1[k], dict2[k])
                if nested_diff:
                    diff[k] = nested_diff
            elif dict1[k] != dict2[k]:
                diff[k] = (dict1[k], dict2[k])
        else:
            diff[k] = (dict1[k], None)
    for k in dict2:
        if k not in dict1:
            diff[k] = (None, dict2[k])
    return diff


def format_amount(number, decimal_point=0):
    if decimal_point > 0:
        amount_string = str(round(float(number), decimal_point))
    else:
        amount_string = str(int(float(number)))
    if "." in amount_string:
        amount_string, decimal_part = amount_string.split(".")
    else:
        decimal_part = ""
    if len(amount_string) <= 3:
        return "Rs. " + amount_string + ("." + decimal_part if decimal_part else "")
    base_three = amount_string[-3:]
    remaining = amount_string[:-3]
    parts = []
    for i in range(0, len(remaining), 2):
        if i == 0:
            parts.append(remaining[-2:])
        else:
            parts.append(remaining[-(i + 2) : -i])
    parts = parts[::-1] + [base_three]
    return "Rs. " + ",".join(parts) + ("." + decimal_part if decimal_part else "")


def log_api_call(name, url, method, payload, headers, response, service_name):
    if app_settings.app_logger:
        app_settings.info(
            "API Call Log: %s",
            {
                "type": name,
                "url": url,
                "method": method,
                "request": payload,
                "response": response.text,
                "headers": headers,
                "service_name": service_name,
            },
        )
    if response.status_code in range(200, 300):  # pylint:  disable=no-else-return
        return response.json()
    elif response.status_code in range(400, 499):
        raise BadRequest(response.json())
    raise BadRequest(
        {
            "message": "Something went wrong",
            "description": f"There is problem with {service_name}. We are working hard to fix this issue. Output: {response.text}",
        },
        response.status_code,
    )
