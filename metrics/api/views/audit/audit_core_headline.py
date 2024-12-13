from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

import config
from metrics.api.enums import AppMode
from metrics.data.managers.core_models.headline import CoreHeadlineQuerySet
from metrics.data.models.core_models.headline import CoreHeadline

from .serializers import AuditCoreHeadlineSerializer
from .shared import AUDIT_API_TAG, AuditEndpointPagination


@extend_schema(tags=[AUDIT_API_TAG])
class AuditCoreHeadlineViewSet(viewsets.ReadOnlyModelViewSet):
    """This endpoint can be used to retrieve all `Headline` records based on `metric` including records still under embargo.

    ---

    # Notes

    Note that this endpoint will only return data for headline metrics. If the `metric` provided
    relates to `timeseries` data the request won't return any results because this is an invalid request.

    ---

    ### Timeseries type metrics are invalid

    For example, a request for the following would be **invalid**

    - metric `COVID-19_cases_casesByDay`

    - geography_type `Nation`

    - geography `England`

    - age `all`

    - sex `all`

    - stratum `default`

    This would be **invalid** because the `metric` of `COVID-19_cases_casesByDay` relates to `timeseries` data.

    ---

    Whereas, a request for the following would be **valid**:

    - metric `COVID-19_headline_ONSdeaths_7DayChange`

    - geography_type `Nation`

    - geography `England`

    - age `all`

    - sex `all`

    - stratum `default`

    This would be **valid** because the `metric` of `COVID-19_headline_ONSdeaths_7DayChange` relates to headline data.

    Note the key difference here being the 2nd part of the metric naming:

    *<topic>* *<metric group>* *<description>*

    A valid metric name for this endpoint should include `headline` as the metric group part of the name.

    """

    permission_classes = []
    queryset = CoreHeadline.objects.all()
    serializer_class = AuditCoreHeadlineSerializer
    pagination_class = AuditEndpointPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self) -> list[type[permissions.BasePermission]]:
        if config.APP_MODE == AppMode.CMS_ADMIN.value:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()

    def get_queryset(self) -> CoreHeadlineQuerySet:
        queryset = super().get_queryset()

        return queryset.filter_headlines_for_audit_list(
            metric_name=self.kwargs["metric"],
            geography_type_name=self.kwargs["geography_type"],
            geography_name=self.kwargs["geography"],
            stratum_name=self.kwargs["stratum"],
            sex=self.kwargs["sex"],
            age=self.kwargs["age"],
        )
