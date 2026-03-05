import datetime

import freezegun
import pytest
from rest_framework.test import APIClient

from ingestion.file_ingestion import data_ingester

EXPECTED_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class TestIngestion:
    @property
    def geography_code(self) -> str:
        return "E12000001"

    @property
    def cold_alert_payload(self) -> dict[str, str | list[dict]]:
        return {
            "parent_theme": "extreme_event",
            "child_theme": "weather_alert",
            "topic": "Cold-alert",
            "metric_group": "headline",
            "metric": "cold-alert_headline_matrixNumber",
            "geography_type": "Government Office Region",
            "geography": "North East",
            "geography_code": self.geography_code,
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "data": [
                {
                    "period_start": "2025-01-01 15:00:00",
                    "period_end": "2025-01-07 08:00:00",
                    "metric_value": 11,
                    "embargo": None,
                    "is_public": True,
                }
            ],
            "refresh_date": "2025-06-11 11:15:00",
        }

    @pytest.mark.django_db
    @freezegun.freeze_time("2025-01-04 12:00:00")
    def test_currently_live_alert_window_can_be_shortened(self):
        """
        Given an existing alert which is currently live
        When a new alert is ingested with a shorter/earlier `period_end`
        Then the alerts/ API returns the newer shorter alert
        """
        # Given
        data_ingester(data=self.cold_alert_payload)
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)

        # Check that we have ingested the original alert
        # and it is being returned by the API correctly
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == "2025-01-07 08:00:00"
        )

        # When
        # A new alert is set with a shorter period_end
        # for an earlier day
        shortened_period_end = "2025-01-05 04:00:00"
        shortened_alert_headline_data = self._mutate_headline_data(
            period_end=shortened_period_end
        )
        data_ingester(data=shortened_alert_headline_data)

        # Then
        # Check that we have ingested the updated alert
        # which reduces `period_end` window but keeps the alert level as the original level
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == shortened_period_end
        )

    @pytest.mark.django_db
    @freezegun.freeze_time("2025-01-04 12:00:00")
    def test_currently_live_alert_window_can_be_shortened_for_the_same_day(self):
        """
        Given an existing alert which is currently live
        When a new alert is ingested with a shorter/earlier `period_end`
            for the same day
        Then the alerts/ API returns the newer shorter alert
        """
        # Given
        data_ingester(data=self.cold_alert_payload)
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)

        # Check that we have ingested the original alert
        # and it is being returned by the API correctly
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == "2025-01-07 08:00:00"
        )

        # When
        # A new alert is set with a shorter period_end on the same day
        shortened_period_end_same_day = "2025-01-07 02:00:00"
        shortened_alert_headline_data = self._mutate_headline_data(
            period_end=shortened_period_end_same_day
        )
        data_ingester(data=shortened_alert_headline_data)

        # Then
        # Check that we have ingested the updated alert
        # which reduces `period_end` window but keeps the alert level as the original level
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == shortened_period_end_same_day
        )

    @pytest.mark.django_db
    @freezegun.freeze_time("2025-01-04 12:00:00")
    def test_currently_live_alert_window_can_be_extended(self):
        """
        Given an existing alert which is currently live
        When a new alert is ingested with a longer/later `period_end`
        Then the alerts/ API returns the newer extended alert
        """
        # Given
        data_ingester(data=self.cold_alert_payload)
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)

        # Check that we have ingested the original alert
        # and it is being returned by the API correctly
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == "2025-01-07 08:00:00"
        )

        # When
        # A new alert is set with an extended period_end
        increased_period_end = "2025-06-12 11:15:00"
        extended_alert_headline_data = self._mutate_headline_data(
            period_end=increased_period_end
        )
        data_ingester(data=extended_alert_headline_data)

        # Then
        # Check that we have ingested the updated alert
        # which increases the `period_end` window
        # but keeps the alert level as the original level
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == increased_period_end
        )

    @pytest.mark.django_db
    @freezegun.freeze_time("2025-01-04 12:00:00")
    def test_currently_live_alert_level_can_be_updated(self):
        """
        Given an existing alert which is currently live
        When a new alert is ingested with an increased `metric_value`
        Then the alerts/ API returns the newer raised alert level
        """
        # Given
        data_ingester(data=self.cold_alert_payload)
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)

        # Check that we have ingested the original alert
        # and it is being returned by the API correctly
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == "2025-01-07 08:00:00"
        )

        # When
        updated_alert_level = 16
        updated_alert_level_headline_data = self._mutate_headline_data(
            metric_value=updated_alert_level
        )
        data_ingester(data=updated_alert_level_headline_data)

        # Then
        # Check that we have ingested the updated alert
        # which keeps the `period_end` window but increases the alert level
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)
        assert response_data["risk_score"] == updated_alert_level
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == self.cold_alert_payload["data"][0]["period_end"]
        )

    @pytest.mark.django_db
    @freezegun.freeze_time("2025-01-04 12:00:00")
    def test_currently_live_alert_level_can_be_cancelled(self):
        """
        Given an existing alert which is currently live
        When a new alert is ingested which sets the `metric_value` to 1
            which therefore cancels the alert
        Then the alerts/ API returns the newer 'cancelled' alert level
        """
        # Given
        data_ingester(data=self.cold_alert_payload)
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)

        # Check that we have ingested the original alert
        # and it is being returned by the API correctly
        assert (
            response_data["risk_score"]
            == self.cold_alert_payload["data"][0]["metric_value"]
        )
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == "2025-01-07 08:00:00"
        )

        # When
        current_time_period_end = "2025-01-04 12:00:00"
        updated_alert_level = 1
        updated_alert_level_headline_data = self._mutate_headline_data(
            metric_value=updated_alert_level,
            period_end=current_time_period_end,
        )
        data_ingester(data=updated_alert_level_headline_data)

        # Then
        # Check that we have ingested the updated alert
        # which sets the `period_end` to the current time
        # and drops the alert level
        response_data = self._hit_alert_endpoint(geography_code=self.geography_code)
        assert response_data["risk_score"] == 1
        assert (
            response_data["period_end"].strftime(EXPECTED_TIMESTAMP_FORMAT)
            == current_time_period_end
        )

    def _mutate_headline_data(
        self, *, period_end: str | None = None, metric_value: int | None = None
    ) -> dict:
        updated_headline_data = self.cold_alert_payload
        metric_value: int = (
            metric_value or self.cold_alert_payload["data"][0]["metric_value"]
        )
        period_end: str = period_end or self.cold_alert_payload["data"][0]["period_end"]

        updated_headline_data["data"][0]["period_end"] = period_end
        updated_headline_data["data"][0]["metric_value"] = metric_value
        updated_headline_data["refresh_date"] = "2025-06-12 11:15:00"

        return updated_headline_data

    @classmethod
    def _hit_alert_endpoint(
        cls, *, geography_code: str
    ) -> dict[str, str | int | datetime.datetime]:
        path = f"/api/alerts/v1/cold/{geography_code}"
        client = APIClient()
        response = client.get(path=path)
        return response.data
