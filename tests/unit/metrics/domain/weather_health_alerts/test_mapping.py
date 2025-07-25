from unittest import mock

import pytest

from metrics.domain.weather_health_alerts import mapping
from metrics.domain.weather_health_alerts.mapping import WeatherHealthAlertTopics
from metrics.domain.weather_health_alerts.text_lookups import (
    cold_alert_text,
    common,
    heat_alert_text,
)


class TestWeatherHealthAlertsMetricMapping:
    @pytest.mark.parametrize(
        "metric_value, expected_status_colour",
        (
            [1, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [2, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [3, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [4, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [5, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [6, mapping.WeatherHealthAlertStatusColour.GREEN.value],
            [7, mapping.WeatherHealthAlertStatusColour.YELLOW.value],
            [8, mapping.WeatherHealthAlertStatusColour.YELLOW.value],
            [9, mapping.WeatherHealthAlertStatusColour.YELLOW.value],
            [10, mapping.WeatherHealthAlertStatusColour.YELLOW.value],
            [11, mapping.WeatherHealthAlertStatusColour.YELLOW.value],
            [12, mapping.WeatherHealthAlertStatusColour.AMBER.value],
            [13, mapping.WeatherHealthAlertStatusColour.AMBER.value],
            [14, mapping.WeatherHealthAlertStatusColour.AMBER.value],
            [15, mapping.WeatherHealthAlertStatusColour.AMBER.value],
            [16, mapping.WeatherHealthAlertStatusColour.RED.value],
        ),
    )
    def test_associated_status_colour(
        self, metric_value: int, expected_status_colour: str
    ):
        """
        Given a metric_value between 1 and 16
        When the `associated_status_colour` property
            is called from an instance of `WeatherHealthAlertsMetricMapping`
        Then the correct status colour is returned
        """
        # Given
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name=mock.Mock(),
        )

        # When
        associated_status_colour: str = (
            weather_health_alerts_mapping.associated_status_colour
        )

        # Then
        assert associated_status_colour == expected_status_colour

    @pytest.mark.parametrize(
        "metric_value, expected_text",
        (
            [1, common.LEVELS_1_TO_4_TEXT],
            [2, common.LEVELS_1_TO_4_TEXT],
            [3, common.LEVELS_1_TO_4_TEXT],
            [4, common.LEVELS_1_TO_4_TEXT],
            [5, common.LEVEL_5_TEXT],
            [6, cold_alert_text._LEVEL_6_TEXT],
            [7, cold_alert_text._LEVEL_7_TEXT],
            [8, cold_alert_text._LEVEL_8_TEXT],
            [9, cold_alert_text._LEVEL_9_TEXT],
            [10, cold_alert_text._LEVEL_10_TEXT],
            [11, cold_alert_text._LEVEL_11_TEXT],
            [12, cold_alert_text._LEVEL_12_TEXT],
            [13, cold_alert_text._LEVEL_13_TEXT],
            [14, cold_alert_text._LEVEL_14_TEXT],
            [15, cold_alert_text._LEVEL_15_TEXT],
            [16, cold_alert_text._LEVEL_16_TEXT],
        ),
    )
    def test_associated_text_for_cold_alerts(
        self, metric_value: int, expected_text: str
    ):
        """
        Given a metric_value between 1 and 16
        And a topic of "Cold-alert"
        When the `associated_text` property
            is called from an instance of `WeatherHealthAlertsMetricMapping`
        Then the correct text is returned for a cold alert
        """
        # Given
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name=WeatherHealthAlertTopics.COLD_ALERT.value,
        )

        # When
        associated_text: str = weather_health_alerts_mapping.associated_text

        # Then
        assert associated_text == expected_text

    @pytest.mark.parametrize(
        "metric_value, expected_text",
        (
            [1, common.LEVELS_1_TO_4_TEXT],
            [2, common.LEVELS_1_TO_4_TEXT],
            [3, common.LEVELS_1_TO_4_TEXT],
            [4, common.LEVELS_1_TO_4_TEXT],
            [5, common.LEVEL_5_TEXT],
            [6, heat_alert_text._LEVEL_6_TEXT],
            [7, heat_alert_text._LEVEL_7_TEXT],
            [8, heat_alert_text._LEVEL_8_TEXT],
            [9, heat_alert_text._LEVEL_9_TEXT],
            [10, heat_alert_text._LEVEL_10_TEXT],
            [11, heat_alert_text._LEVEL_11_TEXT],
            [12, heat_alert_text._LEVEL_12_TEXT],
            [13, heat_alert_text._LEVEL_13_TEXT],
            [14, heat_alert_text._LEVEL_14_TEXT],
            [15, heat_alert_text._LEVEL_15_TEXT],
            [16, heat_alert_text._LEVEL_16_TEXT],
        ),
    )
    def test_associated_text_for_heat_alerts(
        self, metric_value: int, expected_text: str
    ):
        """
        Given a metric_value between 1 and 16
        And a topic of "Heat-alert"
        When the `associated_text` property
            is called from an instance of `WeatherHealthAlertsMetricMapping`
        Then the correct text is returned for a heat alert
        """
        # Given
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name=WeatherHealthAlertTopics.HEAT_ALERT.value,
        )

        # When
        associated_text: str = weather_health_alerts_mapping.associated_text

        # Then
        assert associated_text == expected_text

    def test_associated_text_for_invalid_topic_returns_empty_string(self):
        """
        Given an invalid topic name
        When the `associated_text` property
            is called from an instance of `WeatherHealthAlertsMetricMapping`
        Then an empty string is returned
        """
        # Given
        topic_name = "Invalid-topic"
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=1,
            topic_name=topic_name,
        )

        # When
        associated_text: str = weather_health_alerts_mapping.associated_text

        # Then
        assert associated_text == ""

    @pytest.mark.parametrize(
        "metric_value, expected_impact_value",
        (
            [
                (
                    1,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    2,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    3,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    4,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (5, mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value),
                (6, mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value),
                (7, mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value),
                (8, mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value),
                (
                    9,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    10,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    11,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    12,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    13,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    14,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    15,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    16,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
            ]
        ),
    )
    def test_associated_text_for_impact_level(
        self,
        metric_value: int,
        expected_impact_value: str,
    ):
        """
        Given a valid `metric_value`, an integer between 1 & 16
        When the `associated_impact_level` property is called
            from an instance of `WeatherHealthAlertsMetricMapping`
        Then the correct impact level is returned
        """
        # Given
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name="Heat-alert",
        )

        # When
        associated_impact_level = weather_health_alerts_mapping.associated_impact_level

        # Then
        assert associated_impact_level == expected_impact_value

    def test_impact_level_returns_as_empty_string_with_invalid_metric_value(self):
        """
        Given an invalid `metric_value` an integer outside the range of 1 - 16
        When the `associated_impact_level` property is called
            from an instance of `WeatherHealthAlertsMetricMapping`
        Then an empty string is returned
        """
        # Given
        metric_value = 17
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name="Heat-alert",
        )

        # When
        associated_impact_level = weather_health_alerts_mapping.associated_impact_level

        # Then
        assert associated_impact_level == ""

    @pytest.mark.parametrize(
        "metric_value, expected_likelihood_value",
        (
            [
                (
                    1,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    2,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value,
                ),
                (
                    3,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    4,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    5,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    6,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value,
                ),
                (
                    7,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    8,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    9,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    10,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value,
                ),
                (
                    11,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.VERY_LOW_LEVEL.value,
                ),
                (
                    12,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    13,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
                (
                    14,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.LOW_LEVEL.value,
                ),
                (
                    15,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.MEDIUM_LEVEL.value,
                ),
                (
                    16,
                    mapping.WeatherHealthAlertImpactAndLikelihoodLevel.HIGH_LEVEL.value,
                ),
            ]
        ),
    )
    def test_associated_text_for_likelihood_level(
        self,
        metric_value: int,
        expected_likelihood_value: str,
    ):
        """
        Given a valid `metric_value`, an integer between 1 & 16
        When the `associated_likelihood_level` property is called
            from an instance of `WeatherHealthAlertsMetricMapping`
        Then the correct likelihood level is returned
        """
        # Given
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name="Heat-alert",
        )

        # When
        associated_likelihood_level = (
            weather_health_alerts_mapping.associated_likelihood_level
        )

        # Then
        assert associated_likelihood_level == expected_likelihood_value

    def test_likelihood_level_returns_as_empty_string_with_invalid_metric_value(self):
        """
        Given an invalid `metric_value` an integer outside the range of 1 - 16
        When the `associated_impact_level` property is called
            from an instance of `WeatherHealthAlertsMetricMapping`
        Then an empty string is returned
        """
        # Given
        metric_value = 17
        weather_health_alerts_mapping = mapping.WeatherHealthAlertsMetricMapping(
            metric_value=metric_value,
            topic_name="Heat-alert",
        )

        # When
        associated_likelihood_level = (
            weather_health_alerts_mapping.associated_likelihood_level
        )

        # Then
        assert associated_likelihood_level == ""
