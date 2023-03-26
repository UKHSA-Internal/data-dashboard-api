from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, response, viewsets

from metrics.api.serializers import APITimeSeriesSerializer, DashboardSerializer
from metrics.data.access.generate_dashboard import populate_dashboard
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
        "year",
        "epiweek",
        "dt",
    ]


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if "topic" in self.kwargs:
            return populate_dashboard(topic=self.kwargs["topic"])
        return None

    serializer_class = DashboardSerializer
    lookup_field = "topic"

    def retrieve(self, request, *args, **kwargs):
        data = self.get_queryset()
        return response.Response(data)
