from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from metrics.data.managers.api_models.time_series import APITimeSeriesQuerySet
from metrics.data.models.api_models import APITimeSeries

from .serializers import AuditAPITimeSeriesSerializer
from .shared import AUDIT_API_TAG, AuditEndpointPagination


@extend_schema(tags=[AUDIT_API_TAG])
class AuditAPITimeSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """This endpoint can be used to retrieve all `APITimeseries` records based on `metric` including records
        still under embargo.

    ---

    # Notes

    Note that this endpoint will only return data for `APITimeseries` metrics. If the `metric` provided relates to
    `Headline` data the request won't return any results because this is an invalid request.

    ---

    ### Headline type metrics are invalid.

    For example, a request for the following would be **invalid**

    - metric `COVID-19_headline_ONSDeaths_7DayChange`

    - geography_type `Nation`

    - geography `England`

    - age `all`

    - sex `all`

    - stratum `default`

    This would be **invalid** because the `metric` of `COVID-19_headline_ONSDeaths_7DayChange` relates to `Headline`
    data.

    ---

    Whereas, a request for the following would be **valid**:

    - metric `COVID-19_cases_casesByDay`

    - geography_type `Nation`

    - geography `England`

    - age `all`

    - sex `all`

    - stratum `default`

    This would be a **valid** request because the `metric` of `COVID-19_cases_casesByDay` relates to `Timeseries` data.

    Note the key difference here being the 2nd part of the metric name:

    *<topic>* *<metric group>* *<description>*

    A valid metric name for this endpoint should **NOT** include `headline` as the metric group part of the name.

    """

    permission_classes = []
    queryset = APITimeSeries.objects.all().order_by("date")
    serializer_class = AuditAPITimeSeriesSerializer
    pagination_class = AuditEndpointPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self) -> APITimeSeriesQuerySet:
        queryset = super().get_queryset()

        return queryset.filter_for_audit_list_view(
            metric_name=self.kwargs["metric"],
            geography_name=self.kwargs["geography"],
            geography_type_name=self.kwargs["geography_type"],
            stratum=self.kwargs["stratum"],
            sex=self.kwargs["sex"],
            age=self.kwargs["age"],
        )
