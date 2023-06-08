# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib import admin

from drf_misc.settings import app_settings

# pylint: disable=super-with-arguments,no-member


class ListAdminMixin:
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


if app_settings.ADD_ALL_MODELS_IN_ADMIN:
    models = apps.get_models()
    for i in models:
        AdminClass = type("AdminClass", (ListAdminMixin, admin.ModelAdmin), {})
        try:
            admin.site.register(i, AdminClass)
        except admin.sites.AlreadyRegistered as e:
            pass
