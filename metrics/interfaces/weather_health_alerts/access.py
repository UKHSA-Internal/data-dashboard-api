import logging

from django.db.models.manager import Manager
from django.utils import timezone

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.weather_health_alerts.state import WeatherHealthAlarmState

logger = logging.getLogger(__name__)

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
WEATHER_HEALTH_ALERT_DETAILED_DATA = dict[str, str | None]


class WeatherHealthAlertsInterface:
    def __init__(self, core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER):
        self._core_headline_manager = core_headline_manager

    def build_summary_data_for_alerts(
        self, geography_codes: list[str], topic_name: str, metric_name: str
    ) -> dict[str, WEATHER_HEALTH_ALERT_DETAILED_DATA]:
        """Builds the exported summary data required for each current alert state associated with each `geography_code`

        Args:
            topic_name: The name of the topic
                associated with the alert
            metric_name: The name of the metric
                associated with the alert
            geography_codes: The codes for each of the geographies
                being queried for.

        Returns:
            Dict keyed by the geography_code
            where the values are the exported data
            required to represent each alert

        """
        headlines_mapping = (
            self._core_headline_manager.get_latest_headlines_for_geography_codes(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_codes=geography_codes,
            )
        )

        weather_health_alarm_states = {
            geography_code: self._parse_core_headline_as_alarm_state(
                topic_name=topic_name, core_headline=core_headline
            )
            for geography_code, core_headline in headlines_mapping.items()
        }

        return {
            geography_code: alarm_state.summary_data
            for geography_code, alarm_state in weather_health_alarm_states.items()
        }

    def build_detailed_data_for_alert(
        self, topic_name: str, metric_name: str, geography_code: str
    ) -> WEATHER_HEALTH_ALERT_DETAILED_DATA:
        """Builds the exported data required for the alert associated with the given `core_headline`

        Args:
            topic_name: The name of the topic
                associated with the alert
            metric_name: The name of the metric
                associated with the alert
            geography_code: The code of the geography
                associated with the individual alert

        Returns:
            Dict containing the exported data required to
            represent the alert

        """
        weather_health_alarm_state: WeatherHealthAlarmState = (
            self._build_current_headline_state(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_code=geography_code,
            )
        )
        return weather_health_alarm_state.detailed_data

    def _build_current_headline_state(
        self, topic_name: str, metric_name: str, geography_code: str
    ) -> WeatherHealthAlarmState:
        core_headline: CoreHeadline | None = (
            self._core_headline_manager.get_latest_headline(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_code=geography_code,
            )
        )

        return self._parse_core_headline_as_alarm_state(
            topic_name=topic_name, core_headline=core_headline
        )

    @classmethod
    def _parse_core_headline_as_alarm_state(
        cls, topic_name: str, core_headline: CoreHeadline | None
    ) -> WeatherHealthAlarmState:
        if core_headline is None:
            # In this case, there has never been an alert for this
            # topic/metric/geography_code combination.
            # So we will default to green/normal with null for the timestamps
            return WeatherHealthAlarmState(
                metric_value=1,
                topic_name=topic_name,
                period_start=None,
                period_end=None,
                refresh_date=None,
            )

        if core_headline.period_end <= timezone.now():
            # The last refresh is considered to be when the previous period_end expired
            # In this case, we fall back to the green/normal state of metric_value=1
            refresh_date = core_headline.period_end
            return WeatherHealthAlarmState(
                metric_value=1,
                topic_name=topic_name,
                period_start=core_headline.period_start,
                period_end=core_headline.period_end,
                refresh_date=refresh_date,
            )

        # There is a valid alert which is currently live
        # so we can safely use everything we get from the db record
        return WeatherHealthAlarmState(
            metric_value=core_headline.metric_value,
            topic_name=topic_name,
            period_start=core_headline.period_start,
            period_end=core_headline.period_end,
            refresh_date=core_headline.refresh_date,
        )
