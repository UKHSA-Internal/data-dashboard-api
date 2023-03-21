from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, viewsets

from metrics.api.serializers import APITimeSeriesSerializer
from metrics.data.models.api_models import APITimeSeries


class APITimeSeriesPagination(pagination.PageNumberPagination):
    page_size = 5
    max_page_size = 53


class APITimeSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint can be used to retrieve data for weekly time series of a given topic.

    Note that this data is updated on a weekly basis.
    By default, the list endpoint will paginate by a page size of 5.

    """

    queryset = APITimeSeries.objects.all().order_by("dt")
    serializer_class = APITimeSeriesSerializer
    pagination_class = APITimeSeriesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "theme",
        "sub_theme",
        "topic",
        "geography_type",
        "geography",
        "metric",
        "stratum",
        "sex",
        "dt",
    ]
