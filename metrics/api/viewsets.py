from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import pagination, response, viewsets
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import APITimeSeriesSerializer, DashboardSerializer
from metrics.data.access.generate_dashboard import populate_dashboard
from metrics.data.models.api_models import APITimeSeries


class APITimeSeriesPagination(pagination.PageNumberPagination):
    page_size = 5
    max_page_size = 53


class APITimeSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint can be used to retrieve data for time series of a given topic/metric/date combination.

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
        "year",
        "epiweek",
        "dt",
    ]
    permission_classes = [HasAPIKey]


DEPRECATION_DATE_STATS_ENDPOINT = "Wed, 19 Apr 2023 23:59:59 GMT"
DEPRECATION_MESSAGE_STATS = f"This endpoint has been deprecated. This functionality can now be found within the `/headlines/v2/` and `/trends/v2/ endpoints. Deprecation date: {DEPRECATION_DATE_STATS_ENDPOINT}"

DEPRECATION_HEADERS_STATS = {
    "Deprecation": DEPRECATION_DATE_STATS_ENDPOINT,
    "Message": DEPRECATION_MESSAGE_STATS,
}


class DashboardViewSet(viewsets.GenericViewSet):
    """
    This endpoint can be used to retrieve headline statistics associated with a given topic

    Where there is 1 mandatory param of `topic`, which relates to a type of disease.

    Note that currently only the following topics are supported:

    - `COVID-19`

    - `Influenza`

    For any another `topic` value which is not listed above, an empty array will be returned.
    """

    permission_classes = [HasAPIKey]

    def get_queryset(self):
        if "topic" in self.kwargs:
            return populate_dashboard(topic=self.kwargs["topic"])
        return None

    serializer_class = DashboardSerializer
    lookup_field = "topic"

    @extend_schema(deprecated=True)
    def retrieve(self, request, *args, **kwargs):
        data = self.get_queryset()
        return response.Response(data, headers=DEPRECATION_HEADERS_STATS)
