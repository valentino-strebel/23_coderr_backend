"""
@file pagination.py
@description
    Defines custom pagination for offers using DRF's PageNumberPagination.
"""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    @pagination OfferPagination
    @extends PageNumberPagination
    @description
        Custom paginator for offers. Uses page number pagination with
        configurable page size.

    @config
        page_size {int} = 10          Default number of results per page
        page_size_query_param = "page_size"  Query parameter to control page size
        max_page_size {int} = 100     Maximum allowed page size
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
