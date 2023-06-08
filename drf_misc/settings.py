# -*- coding: utf-8 -*-
from django.conf import settings

# pylint: disable=invalid-name


class AppSettings:
    def __init__(self):
        self.app_settings = getattr(settings, "DRF_MISC_SETTINGS", {})

    @property
    def service_name(self):
        """Control how many times a task will be attempted."""
        return self.app_settings.get("service_name", "django_extra")

    @property
    def audit_queue_url(self):
        """Control how many times a task will be attempted."""
        return self.app_settings.get("audit_queue_url", {})

    @property
    def use_service_cache(self):
        return self.app_settings.get("use_service_cache", False)

    @property
    def auth_check_disabled_paths(self):
        return self.app_settings.get("auth_check_disabled_paths", [])


app_settings = AppSettings()

TIME_ZONE = "Asia/Kolkata"
