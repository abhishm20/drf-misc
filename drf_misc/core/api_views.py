# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import NestedViewSetMixin

from drf_misc.core.api_exceptions import BadRequest
from drf_misc.core.filter_backend import FlexFieldsFilterBackend

# pylint: disable=unused-argument,no-member, protected-access


class FlexFieldsMixin:
    permit_list_expands = []
    _expandable = True
    _force_expand = []

    def list(self, request, *args, **kwargs):
        self._expandable = False
        expand = request.query_params.get("expand")

        if len(self.permit_list_expands) > 0 and expand:
            if expand == "~all":
                self._force_expand = self.permit_list_expands
            else:
                self._force_expand = list(set(expand.split(",")) & set(self.permit_list_expands))
        if hasattr(super(), "list") and super().list:
            return super().list(request, *args, **kwargs)
        raise BadRequest({"message": "Method not allowed"})

    def get_serializer_class(self):
        """Dynamically adds properties to serializer_class from request's GET params."""
        expand = None
        fields = None
        is_valid_request = hasattr(self, "request") and self.request and self.request.method == "GET"

        if not is_valid_request:
            return self.serializer_class

        fields = self.request.query_params.get("fields")
        if not fields and hasattr(self, "fields"):
            fields = self.fields
        fields = fields.split(",") if fields else None

        if self._expandable:
            expand = self.request.query_params.get("expand")
            if not expand and hasattr(self, "expand"):
                expand = self.expand
            expand = expand.split(",") if expand else None
        elif len(self._force_expand) > 0:
            expand = self._force_expand
        if self.serializer_class:
            return type(
                str("Serializer"),
                (self.serializer_class,),
                {"expand": expand, "include_fields": fields},
            )
        return None


class RelationalGenericViewSet(NestedViewSetMixin, FlexFieldsMixin, viewsets.GenericViewSet):
    filter_backends = (FlexFieldsFilterBackend,)

    def get_queryset(self):
        assert self.queryset is not None, (
            f"'{self.__class__.__name__}' should either include "
            f"a `queryset` attribute, or override the `get_queryset()` method."
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        filter_kwargs = {}
        if hasattr(self, "relational_filter"):
            for key, value in self.relational_filter.items():
                filter_kwargs.update({key: self.kwargs[value]})
            queryset = queryset.filter(**filter_kwargs)
        return queryset

    def make_request_mutable(self, request):
        if hasattr(request.data, "_mutable"):
            request.data._mutable = True
        if hasattr(request.GET, "_mutable"):
            request.GET._mutable = True

    @action(detail=False, methods=["GET"], url_path="_refresh_cache")
    def _refresh_cache(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for instance in queryset:
            instance = self.service_class(instance=instance).set_cache(raise_exception=True)
        return Response({"message": "Successfully refreshed"})


class DestroyMM(RelationalGenericViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, request=None):
        if hasattr(self, "service_class") and self.service_class:
            self.service_class(instance.id).delete(request=request)
        else:
            instance.delete()


class CreateMM(RelationalGenericViewSet):
    """
    Create a model instance.
    """

    def create(self, request, **kwargs):
        self.make_request_mutable(request)
        if hasattr(self, "service_class") and self.service_class:
            instance = self.service_class().create(request.data, request=request)
            serializer = self.get_serializer(instance)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ListMM(RelationalGenericViewSet):
    """
    List a queryset.
    """

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get("no-pagination"):
            self.pagination_class = None
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InternalMM(RelationalGenericViewSet):
    @action(detail=False, methods=["PUT"], url_path="bulk/internal", permission_classes=[], authentication_classes=[])
    def bulk_internal(self, request, *args, **kwargs):
        if request.data.get("ids"):
            queryset = self.model.objects.filter(id__in=request.data.get("ids"))
        elif request.data.get("ref_ids"):
            queryset = self.model.objects.filter(ref_id__in=request.data.get("ref_ids"))
        serializer = self.serializer_class(
            queryset,
            many=True,
            expand=request.data.get("expand", ""),
            fields=request.data.get("fields", ""),
        )
        return Response(serializer.data)


class RetrieveMM(RelationalGenericViewSet):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UpdateMM(RelationalGenericViewSet):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        self.make_request_mutable(request)
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if hasattr(self, "service_class") and self.service_class:
            instance = self.service_class(instance.id).update(request.data, request=request, partial=partial)
            serializer = self.get_serializer(instance)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


def filter_queryset_by_auth(queryset, auth_data, is_root, company_programs=None):
    if auth_data.get("lead_id"):
        if is_root:
            queryset = queryset.filter(crm_lead_id=auth_data["lead_id"])
        else:
            queryset = queryset.filter(account__crm_lead_id=auth_data["lead_id"])
    elif auth_data.get("program_id"):
        if is_root:
            queryset = queryset.filter(program_id=auth_data["program_id"])
        else:
            queryset = queryset.filter(account__program_id=auth_data["program_id"])
    elif auth_data.get("company_id"):
        if company_programs:
            program_ids = [program["id"] for program in company_programs]
        else:
            program_ids = []
        if is_root:
            queryset = queryset.filter(program_id__in=program_ids)
        else:
            queryset = queryset.filter(account__program_id__in=program_ids)
    return queryset
