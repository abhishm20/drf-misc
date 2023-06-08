# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import inspect

import jwt
from django.utils.deprecation import MiddlewareMixin

from drf_misc.settings import app_settings

# pylint: disable=inconsistent-return-statements


def get_current_request():
    """Walk up the stack, return the nearest first argument named "request"."""
    frame = None
    try:
        for _f in inspect.stack()[1:]:
            frame = _f[0]
            code = frame.f_code
            if code.co_varnames and code.co_varnames[0] == "request":
                return frame.f_locals["request"]
    finally:
        del frame


class DisableCsrfCheck(MiddlewareMixin):
    def process_request(self, request):
        attr = "_dont_enforce_csrf_checks"
        if not getattr(request, attr, False):
            setattr(request, attr, True)


class AuthTokenHandler(MiddlewareMixin):
    def process_request(self, request):
        header_session = request.META.get("HTTP_AUTHORIZATION")
        query_session = request.GET.get("auth")
        if header_session:
            request.COOKIES.update({"sessionid": header_session})
        if query_session:
            request.COOKIES.update({"sessionid": query_session})


class AuthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        for path in app_settings.auth_check_disabled_paths:
            if path in request.build_absolute_uri():
                return
        token = request.META.get("HTTP_AUTHORIZATION")
        valid_data = {}
        if token:
            token = token.replace("Bearer ", "")
            valid_data = jwt.decode(token, options={"verify_signature": False})
        request.auth_user = valid_data
