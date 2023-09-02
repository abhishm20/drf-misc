# -*- coding: utf-8 -*-
from rest_framework import permissions


class IsSuperUserPermission(permissions.BasePermission):
    edit_methods = ("PUT", "PATCH", "POST")

    def has_permission(self, request, view):
        if request.user.is_authenticated and not request.user.is_superuser and request.method in self.edit_methods:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return True
