# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import inspect

import jwt
from django.http import JsonResponse
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
            if path in request.path:
                return

        token = request.META.get("HTTP_AUTHORIZATION")
        valid_data = {}
        if token:
            token = token.replace("Bearer ", "")
            try:
                valid_data = jwt.decode(token, options={"verify_signature": False})
                request.auth_user = valid_data
            except Exception as error:
                if app_settings.app_logger:
                    app_settings.app_logger.exception(error)
                return JsonResponse({"message": "Authentication failed"})
        else:
            request.auth_user = valid_data


# class JSONResponseMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         return self.process_response(request, response)

#     def process_response(self, request, response):
#         if response.status_code in range(200, 300):
#             return JsonResponse(response, status=response.status_code)

#         elif response.status_code == 400:
#             return JsonResponse(response, status=400)

#         elif response.status_code == 404:
#             try:
#                 if json.loads(response.content).get("message") == "Not found.":
#                     return JsonResponse({"message": "Resource not found."}, status=404)
#             except:
#                 return JsonResponse({"message": "The requested URL was not found."}, status=404)

#         elif response.status_code == 500:
#             return JsonResponse({"message": "An internal server error occurred."}, status=500)

#         return response
