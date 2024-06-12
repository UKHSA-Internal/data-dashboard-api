from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from caching.private_api.decorators import cache_response
from metrics.api.enums import Alerts
from metrics.api.serializers.geographies_alerts import GeographiesForAlertsSerializer
from metrics.interfaces.weather_health_alerts.access import (
    get_detailed_data_for_alert,
    get_summary_data_for_alerts,
)

ALERTS_API_TAG = "alerts"
EIGHT_MINUTES_AS_SECONDS = 60 * 8


@extend_schema(tags=[ALERTS_API_TAG])
class BaseAlertViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = []

    @property
    def topic_name(self) -> str:
        raise NotImplementedError

    @property
    def metric_name(self) -> str:
        raise NotImplementedError

    @cache_response(timeout=EIGHT_MINUTES_AS_SECONDS)
    def list(self, request, *args, **kwargs):
        topic_name: str = self.topic_name
        metric_name: str = self.metric_name

        serializer = GeographiesForAlertsSerializer()
        geography_data = serializer.data()
        summary_data: list[dict[str, str]] = get_summary_data_for_alerts(
            geography_data=geography_data,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        return Response(data=summary_data)

    @cache_response(timeout=EIGHT_MINUTES_AS_SECONDS)
    def retrieve(self, request, *args, **kwargs):
        topic_name: str = self.topic_name
        metric_name: str = self.metric_name

        serializer = GeographiesForAlertsSerializer()
        geography_data = serializer.data()

        geography_code = kwargs["geography_code"]
        payload = {"geography_code": geography_code}
        request_serializer = GeographiesForAlertsSerializer(data=payload)
        request_serializer.is_valid(raise_exception=True)

        geography_data = dict(filter(lambda x: geography_code in x, geography_data))

        summary_data: dict[str, str] = get_detailed_data_for_alert(
            geography_code=geography_code,
            geography_name=geography_data[geography_code],
            geography_type_name=Alerts.ALERT_GEOGRAPHY_TYPE_NAME.value,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        return Response(data=summary_data)


class HeatAlertViewSet(BaseAlertViewSet):
    @property
    def topic_name(self) -> str:
        return Alerts.HEAT_TOPIC_NAME.value

    @property
    def metric_name(self) -> str:
        return Alerts.HEAT_METRIC_NAME.value


class ColdAlertViewSet(BaseAlertViewSet):
    @property
    def topic_name(self) -> str:
        return Alerts.COLD_TOPIC_NAME.value

    @property
    def metric_name(self) -> str:
        return Alerts.COLD_METRIC_NAME.value
