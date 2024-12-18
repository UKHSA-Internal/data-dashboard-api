from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries

from .serializers import AuditCoreTimeseriesSerializer
from .shared import AUDIT_API_TAG, AuditEndpointPagination


@extend_schema(tags=[AUDIT_API_TAG])
class AuditCoreTimeseriesViewSet(viewsets.ReadOnlyModelViewSet):
    """This endpoint can be used to retrieve all `CoreTimeseries` records based on `metric` including records
        still under embargo.

    ---

    # Notes

    Note that this endpoint will only return data for `timeseries` metrics. If the `metric provided
    relates to `Headline` data the request won't return any results because this is an invalid request.

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

    Note the key difference here being the 2nd part of the metric naming:

    *<topic>* *<metric group>* *<description>*

    A valid metric name for this endpoint should **NOT** include `headline` as the metric group part of the name.

    """

    permission_classes = []
    queryset = CoreTimeSeries.objects.all().order_by("date")
    serializer_class = AuditCoreTimeseriesSerializer
    pagination_class = AuditEndpointPagination

    def get_queryset(self) -> CoreTimeSeriesQuerySet:
        queryset = super().get_queryset()

        return queryset.filter_for_audit_list_view(
            metric_name=self.kwargs["metric"],
            geography_type_name=self.kwargs["geography_type"],
            geography_name=self.kwargs["geography"],
            stratum_name=self.kwargs["stratum"],
            sex=self.kwargs["sex"],
            age=self.kwargs["age"],
        )
