from rest_framework import pagination

AUDIT_API_TAG = "Audit"

DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 365
PAGE_SIZE_QUERY_PARAM = "page_size"

EXPECTED_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class AuditEndpointPagination(pagination.PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
