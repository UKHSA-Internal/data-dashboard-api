from enum import Enum

from metrics.domain.weather_health_alerts.text_lookups import (
    COLD_ALERT_TEXT_LOOKUP,
    HEAT_ALERT_TEXT_LOOKUP,
)


class WeatherHealthAlertStatusColour(Enum):
    GREEN = "Green"
    YELLOW = "Yellow"
    AMBER = "Amber"
    RED = "Red"


GREEN_LEVEL_BOUNDARY = 6
YELLOW_LEVEL_BOUNDARY = 11
AMBER_LEVEL_BOUNDARY = 15


class WeatherHealthAlertTopics(Enum):
    HEAT_ALERT = "Heat-alert"
    COLD_ALERT = "Cold-alert"


class WeatherHealthAlertsMetricMapping:
    def __init__(self, *, metric_value: int, topic_name: str):
        self._metric_value = metric_value
        self._topic_name = topic_name

    @property
    def associated_status_colour(self) -> str:
        """Fetch the colour of the associated status

        Notes:
            Can only be one of the following:
                - 'Green'
                - 'Yellow'
                - 'Amber'
                - 'Red'

        Returns:
            A string representation of the associated status colour

        """
        if self._metric_value <= GREEN_LEVEL_BOUNDARY:
            return WeatherHealthAlertStatusColour.GREEN.value
        if self._metric_value <= YELLOW_LEVEL_BOUNDARY:
            return WeatherHealthAlertStatusColour.YELLOW.value
        if self._metric_value <= AMBER_LEVEL_BOUNDARY:
            return WeatherHealthAlertStatusColour.AMBER.value
        return WeatherHealthAlertStatusColour.RED.value

    @property
    def associated_text(self) -> str:
        """Fetch the advice text for the `metric_value` and `topic`

        Returns:
            A string representation of the associated advice text

        """
        match self._topic_name:
            case WeatherHealthAlertTopics.HEAT_ALERT.value:
                return self._associated_heat_alert_text
            case WeatherHealthAlertTopics.COLD_ALERT.value:
                return self._associated_cold_alert_text
        return ""

    @property
    def _associated_cold_alert_text(self) -> str:
        """Fetch the advice text associated with the cold alert

        Returns:
            A string representation of the associated advice text

        """
        return COLD_ALERT_TEXT_LOOKUP.get(self._metric_value, "")

    @property
    def _associated_heat_alert_text(self) -> str:
        """Fetch the advice text associated with the heat alert

        Returns:
            A string representation of the associated advice text

        """
        return HEAT_ALERT_TEXT_LOOKUP.get(self._metric_value, "")
