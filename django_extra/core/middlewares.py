# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import inspect

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from django_extra.settings import app_settings

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


class AppNameMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not app_settings.APP_NAMES:
            return
        if request.GET.get("app-name"):
            request.META["HTTP_X_APP_NAME"] = request.GET.get("x-app-name")

        request.app_name = request.META.get("HTTP_X_APP_NAME")

        if (
            not request.app_name
            and "/admin" not in request.get_full_path()
            and "/callbacks/" not in request.get_full_path()
            and "/status" not in request.get_full_path()
        ):
            return HttpResponseForbidden("x-app-name header is required")

        user = request.user

        if user.is_authenticated:
            if request.app_name not in app_settings.APP_NAMES:
                return HttpResponseForbidden("x-app-name header is invalid")
        return
