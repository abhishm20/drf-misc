# -*- coding: utf-8 -*-
from django.conf import settings

# pylint: disable=invalid-name


class AppSettings:
    def __init__(self):
        self.app_settings = settings.get("DJANGO_EXTRA_SETTINGS", {})

    @property
    def SERVICE_NAME(self):
        """Control how many times a task will be attempted."""
        return getattr(self.app_settings, "SERVICE_NAME", "django_extra")

    @property
    def APP_NAMES(self):
        return getattr(self.app_settings, "APP_NAMES", [])

    @property
    def USE_SERVICE_CACHE(self):
        return getattr(self.app_settings, "USE_SERVICE_CACHE", False)

    @property
    def DATA_UPLOAD_MAX_MEMORY_SIZE(self):
        return getattr(self.app_settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", 5000)


app_settings = AppSettings()
