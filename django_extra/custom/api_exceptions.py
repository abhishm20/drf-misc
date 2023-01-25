# -*- coding: utf-8 -*-
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class BadRequest(APIException):
    status_code = 400
    default_detail = "Request is invalid"
    default_code = "bad_request"


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class ServerError(APIException):
    status_code = 500
    default_detail = "Internal Service Error, try again later."
    default_code = "server_error"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # TODO handle named validation error # pylint: disable=fixme
        response.data["status_code"] = response.status_code
        if response.data.get("detail") and not response.data.get("message"):
            response.data["message"] = response.data["detail"]
            del response.data["detail"]

    return response
