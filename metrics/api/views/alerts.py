from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from metrics.data.models.core_models import Geography
from metrics.interfaces.weather_health_alerts.access import get_summary_data_for_alerts, get_detailed_data_for_alert

ALERTS_API_TAG = "alerts"


class GeographiesForAlertsSerializer(serializers.Serializer):
    @property
    def geography_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Geography` model.
        """
        return self.context.get("geography_manager", Geography.objects)

    def data(self):
        return self.geography_manager.get_all_geography_codes_by_geography_type(
            geography_type_name="Government Office Region"
        )


@extend_schema(tags=[ALERTS_API_TAG])
class BaseAlertViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = []

    @property
    def topic_name(self) -> str:
        raise NotImplementedError

    @property
    def metric_name(self) -> str:
        raise NotImplementedError

    def list(self, request, *args, **kwargs):
        serializer = GeographiesForAlertsSerializer()
        geography_codes = serializer.data()
        summary_data: list[dict[str, str]] = get_summary_data_for_alerts(
            geography_codes=geography_codes,
            topic_name=self.topic_name,
            metric_name=self.metric_name,
        )

        return Response(
            data=summary_data
        )

    def retrieve(self, request, *args, **kwargs):
        summary_data: list[dict[str, str]] = get_detailed_data_for_alert(
            geography_code='E06000001',
            topic_name=self.topic_name,
            metric_name=self.metric_name,
        )

        return Response(
            data=summary_data
        )


class HeatAlertViewSet(BaseAlertViewSet):
    @property
    def topic_name(self) -> str:
        return "Heat-alert"

    @property
    def metric_name(self) -> str:
        return "heat-alert_headline_matrixNumber"
