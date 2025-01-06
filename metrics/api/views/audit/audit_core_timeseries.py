from datetime import datetime, timedelta

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, viewsets

import config
from metrics.api.enums import AppMode
from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries

from .serializers import AuditCoreTimeseriesSerializer
from .shared import AUDIT_API_TAG, AuditEndpointPagination


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.STR,
            description="The date to start your timeseries slice from (defaults to a year ago today)",
            required=False,
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.STR,
            description="The date to end your timeseries slice at (defaults to today's date)",
            required=False,
        ),
    ],
    tags=[AUDIT_API_TAG],
)
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

    def get_permissions(self) -> list[type[permissions.BasePermission]]:
        if AppMode.CMS_ADMIN.value == config.APP_MODE:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    def get_date_from(self) -> str:
        """Returns the date from a year ago from today if query param `date_from` is None
        otherwise it returns the provided `date_from` string
        """
        return (
            self.request.query_params.get("date_from")
            if self.request.query_params.get("date_from") is not None
            else (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        )

    def get_date_to(self) -> str:
        """Returns today's date as a string if query param `date_to` is None
        otherwise it returns the provided `date_to` string
        """
        return (
            self.request.query_params.get("date_to")
            if self.request.query_params.get("date_to") is not None
            else (datetime.now()).strftime("%Y-%m-%d")
        )

    def get_queryset(self) -> CoreTimeSeriesQuerySet:
        queryset = (
            super()
            .get_queryset()
            .filter(
                date__gte=self.get_date_from(),
                date__lte=self.get_date_to(),
            )
        )

        return queryset.filter_for_audit_list_view(
            metric_name=self.kwargs["metric"],
            geography_type_name=self.kwargs["geography_type"],
            geography_name=self.kwargs["geography"],
            stratum_name=self.kwargs["stratum"],
            sex=self.kwargs["sex"],
            age=self.kwargs["age"],
        )
