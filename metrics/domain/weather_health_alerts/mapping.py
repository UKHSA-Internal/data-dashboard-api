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


class WeatherHealthAlertImpactAndLikelihoodLevel(Enum):
    VERY_LOW_LEVEL = "Very low"
    LOW_LEVEL = "Low"
    MEDIUM_LEVEL = "Medium"
    HIGH_LEVEL = "High"


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
    def associated_impact_level(self) -> str:
        """Fetch the impact status for the current `metric_value`

        Returns:
            A string representation of the associated `impact status`
            Eg: `Very low`
        """
        match self._metric_value:
            case 1 | 2 | 3 | 4:
                return WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value
            case 5 | 6 | 7 | 8:
                return WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value
            case 9 | 10 | 11 | 12:
                return WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value
            case 13 | 14 | 15 | 16:
                return WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value
            case _:
                return ""

    @property
    def associated_likelihood_level(self) -> str:
        """Fetch the likelihood status for the current `metric_value`

        Returns:
            A string representation of the associated `likelihood status`
            Eg: `Very low`
        """
        match self._metric_value:
            case 1 | 5 | 9 | 13:
                return WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value
            case 2 | 6 | 10 | 14:
                return WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value
            case 3 | 7 | 11 | 15:
                return WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value
            case 4 | 8 | 12 | 16:
                return WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value
            case _:
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
