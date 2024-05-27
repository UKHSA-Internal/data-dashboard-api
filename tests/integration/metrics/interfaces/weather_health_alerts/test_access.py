import pytest


from metrics.interfaces.weather_health_alerts.access import (
    WeatherHealthAlertsInterface,
    WEATHER_HEALTH_ALERT_DETAILED_DATA,
    get_summary_data_for_alerts,
)

from tests.fakes.factories.metrics.headline_factory import FakeCoreHeadlineFactory
from tests.fakes.managers.headline_manager import FakeCoreHeadlineManager


class TestAccessGetSummaryDataForAlerts:
    @pytest.mark.parametrize(
        "geography_data, topic, metric",
        [
            (
                [("E06000001", "North East"), ("E06000002", "North West")],
                "Heat-alert",
                "heat-alert_headline_matrixNumber",
            )
        ],
    )
    @pytest.mark.django_db
    def test_access_get_summary_data_for_alerts_returns_expected_response(
        self,
        geography_data: list[tuple[str, str]],
        topic: str,
        metric: str,
    ):
        """
        Given A valid list of geography codes and names, a topic and metric name
        When when the `get_summary_data_for_alerts()` method is called
        Then then a list of alert summary details are returned.
        """
        # Given
        fake_geography_data = geography_data
        fake_topic = topic
        fake_metric = metric

        expected_output = [
            {
                "geography_code": "E06000001",
                "geography_name": "North East",
                "status": "Green",
                "refresh_date": None,
            },
            {
                "geography_code": "E06000002",
                "geography_name": "North West",
                "status": "Green",
                "refresh_date": None,
            },
        ]

        # When
        summary_data = get_summary_data_for_alerts(
            geography_data=fake_geography_data,
            topic_name=fake_topic,
            metric_name=fake_metric,
        )

        # then
        assert len(summary_data) == len(expected_output)
