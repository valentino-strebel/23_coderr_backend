from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    page_size = 10  # default
    page_size_query_param = "page_size"
    max_page_size = 100
