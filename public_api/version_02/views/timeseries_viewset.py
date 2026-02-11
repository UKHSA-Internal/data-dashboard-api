import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import pagination, viewsets

from public_api.metrics_interface.interface import MetricsPublicAPIInterface
from public_api.version_02.serializers.timeseries_serializers import (
    APITimeSeriesListSerializerv2,
)
from public_api.version_02.views.base import PUBLIC_API_TAG

DEFAULT_API_TIMESERIES_RESPONSE_PAGE_SIZE: int = 5
MAXIMUM_API_TIMESERIES_RESPONSE_PAGE_SIZE: int = 365


class APITimeSeriesPaginationv2(pagination.PageNumberPagination):
    page_size = DEFAULT_API_TIMESERIES_RESPONSE_PAGE_SIZE
    max_page_size = MAXIMUM_API_TIMESERIES_RESPONSE_PAGE_SIZE
    page_size_query_param = "page_size"


@extend_schema(tags=[PUBLIC_API_TAG])
class APITimeSeriesViewSetV2(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint will provide the full timeseries of a slice of data.

    There are a set of mandatory URL parameters and optional query parameters:

    Note that by default, results are paginated by a page size of 5

    This page size can be changed using the *page_size* parameter.
    The maximum supported page size is **365**.

    ---

    Whereby the mandatory URL parameters are as follows in order from first to last:

    - `theme` - The largest topical subgroup e.g. **infectious_disease**

    - `sub_theme` - A topical subgroup e.g. **respiratory**

    - `topic` - The name of the topic e.g. **COVID-19**

    - `geography_type` - The type of the geography type e.g. **Nation**

    - `geography` - The name of the geography associated with metric  e.g. **London**

    - `metric` - The name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    ---

    From here you can filter the data further via a set of optional query parameters:

    - `stratum` - Smallest subgroup a metric can be broken down into e.g. ethnicity, testing pillar

    - `age` - Smallest subgroup a metric can be broken down into e.g. **15_44** for the age group of 15-44 years

    - `sex` - Patient gender e.g. **f** for Female or **all** for all genders

    - `year` - Epi year of the metrics value (important for annual metrics) e.g. **2020**

    - `month` - Epi month of the metric value (important for monthly metrics) e.g. **12**

    - `epiweek` - Epi week of the metric value (important for weekly metrics) e.g. **30**

    - `date` - The date which this metric value was recorded in the format **YYYY-MM-DD** e.g. **2020-07-20**

    - `in_reporting_delay_period` - A boolean indicating whether the data point is considered to be subject
    to retrospective updates.

    """

    permission_classes = []
    name = "API Time Series Slice"
    queryset = (
        MetricsPublicAPIInterface.get_api_timeseries_model()
        .objects.all()
        .order_by("date")
    )
    serializer_class = APITimeSeriesListSerializerv2
    pagination_class = APITimeSeriesPaginationv2
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "stratum",
        "sex",
        "age",
        "year",
        "epiweek",
        "date",
        "in_reporting_delay_period",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter_for_list_view(
            theme=self.kwargs["theme"],
            sub_theme=self.kwargs["sub_theme"],
            topic=self.kwargs["topic"],
            geography_type=self.kwargs["geography_type"],
            geography=self.kwargs["geography"],
            metric=self.kwargs["metric"],
            restrict_to_public=True,
        )


class APITimeSeriesFilterSetv3(django_filters.FilterSet):
    geography = django_filters.CharFilter(field_name="geography", lookup_expr="iexact")
    geography_type = django_filters.CharFilter(
        field_name="geography_type", lookup_expr="iexact"
    )

    class Meta:
        model = MetricsPublicAPIInterface.get_api_timeseries_model()
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "stratum",
            "sex",
            "age",
            "year",
            "epiweek",
            "date",
            "in_reporting_delay_period",
        ]


@extend_schema(tags=[PUBLIC_API_TAG])
class APITimeSeriesViewSetV3(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint will provide the full timeseries of a slice of data.

    There are only optional query parameters:

    Note that by default, results are paginated by a page size of 100

    This page size can be changed using the *page_size* parameter.
    The maximum supported page size is **365**.

    ---

    The optional query parameters are as follows in order from first to last:

    - `theme` - The largest topical subgroup e.g. **infectious_disease**

    - `sub_theme` - A topical subgroup e.g. **respiratory**

    - `topic` - The name of the topic e.g. **COVID-19**

    - `geography_type` - The type of the geography type e.g. **Nation**

    - `geography` - The name of the geography associated with metric  e.g. **London**

    - `metric` - The name of the metric being queried for e.g. **COVID-19_deaths_ONSByDay**

    - `stratum` - Smallest subgroup a metric can be broken down into e.g. ethnicity, testing pillar

    - `age` - Smallest subgroup a metric can be broken down into e.g. **15_44** for the age group of 15-44 years

    - `sex` - Patient gender e.g. **f** for Female or **all** for all genders

    - `year` - Epi year of the metrics value (important for annual metrics) e.g. **2020**

    - `month` - Epi month of the metric value (important for monthly metrics) e.g. **12**

    - `epiweek` - Epi week of the metric value (important for weekly metrics) e.g. **30**

    - `date` - The date which this metric value was recorded in the format **YYYY-MM-DD** e.g. **2020-07-20**

    - `in_reporting_delay_period` - A boolean indicating whether the data point is considered to be subject
    to retrospective updates.

    """

    permission_classes = []
    name = "API Time Series Version 3"
    queryset = (
        MetricsPublicAPIInterface.get_api_timeseries_model()
        .objects.all()
        .order_by("date")
    )
    serializer_class = APITimeSeriesListSerializerv2
    pagination_class = APITimeSeriesPaginationv2
    page_size = 100
    filter_backends = [DjangoFilterBackend]
    filterset_class = APITimeSeriesFilterSetv3
