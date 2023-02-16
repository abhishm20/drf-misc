# -*- coding: utf-8 -*-
from django.conf import settings

# pylint: disable=invalid-name


class AppSettings:
    def __init__(self):
        self.app_settings = getattr(settings, "DJANGO_EXTRA_SETTINGS", {})

    @property
    def SERVICE_NAME(self):
        """Control how many times a task will be attempted."""
        return self.app_settings.get("SERVICE_NAME", "django_extra")

    @property
    def USE_SERVICE_CACHE(self):
        return self.app_settings.get("USE_SERVICE_CACHE", False)

    @property
    def AUTH_CHECK_DISABLED_PATHS(self):
        return self.app_settings.get("AUTH_CHECK_DISABLED_PATHS", [])


app_settings = AppSettings()
