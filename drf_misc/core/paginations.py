# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from collections import OrderedDict

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

# pylint: disable=no-member,raise-missing-from,inconsistent-return-statements


class NoPagination(PageNumberPagination):
    page_size = sys.maxsize
    max_page_size = sys.maxsize


class Count15Pagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = sys.maxsize

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
            self.first_page = paginator.page(1)
            self.last_page = paginator.page(paginator.num_pages)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(page_number=page_number, message=str(exc))
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True
        self.request = request
        return list(self.page)

    def get_first_page_link(self):
        if self.first_page:
            url = self.request.build_absolute_uri()
            return remove_query_param(url, self.page_query_param)

    def get_last_page_link(self):
        if self.last_page:
            url = self.request.build_absolute_uri()
            page_number = self.page.paginator.num_pages
            return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("current_page", self.page.number),
                    ("page_size", self.get_page_size(self.request)),
                    ("results", data),
                ]
            )
        )
