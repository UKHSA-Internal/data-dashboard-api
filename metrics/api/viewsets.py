from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, viewsets

from metrics.api.models.api_models import WeeklyTimeSeries
from metrics.api.serializers import WeeklyTimeSeriesSerializer


class WeeklyTimeSeriesPagination(pagination.PageNumberPagination):
    page_size = 5
    max_page_size = 53


class WeeklyTimeSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint can be used to retrieve data for weekly time series of a given topic.

    Note that this data is updated on a weekly basis.
    By default, the list endpoint will paginate by a page size of 5.

    """
    queryset = WeeklyTimeSeries.objects.all().order_by("start_date")
    serializer_class = WeeklyTimeSeriesSerializer
    pagination_class = WeeklyTimeSeriesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "theme",
        "sub_theme",
        "topic",
        "geography_type",
        "geography",
        "metric",
        "stratum",
        "year",
        "epiweek",
        "start_date",
    ]
