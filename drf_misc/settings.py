# -*- coding: utf-8 -*-
from django.conf import settings

# pylint: disable=invalid-name

temp_app_settings = getattr(settings, "DRF_MISC_SETTINGS", {})
assert temp_app_settings.get("service_name")


class AppSettings:
    @property
    def service_name(self):
        """Control how many times a task will be attempted."""
        return temp_app_settings.get("service_name", "django_extra")

    @property
    def audit_queue_url(self):
        """Control how many times a task will be attempted."""
        return temp_app_settings.get("audit_queue_url", {})

    @property
    def use_service_cache(self):
        return temp_app_settings.get("use_service_cache", False)

    @property
    def auth_check_disabled_paths(self):
        return temp_app_settings.get("auth_check_disabled_paths", [])

    @property
    def app_logger(self):
        return temp_app_settings.get("app_logger")


app_settings = AppSettings()

TIME_ZONE = "Asia/Kolkata"
