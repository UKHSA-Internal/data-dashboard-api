import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.data.models.core_models import CoreTimeSeries
from metrics.api.views.audit.serializers import AuditCoreTimeseriesSerializer

from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)


class TestCoreTimeSeriesSerializer:

    @staticmethod
    def _setup_fake_times_series():
        return FakeCoreTimeSeriesFactory.build_time_series(
            metric_name="COVID-19_cases_casesByDay",
            topic_name="COVID-19",
            metric_value=2,
            date=datetime.date(day=1, month=1, year=2024),
            refresh_date=datetime.datetime(day=1, month=1, year=2024),
            embargo=datetime.datetime(day=5, month=1, year=2024),
        )

    def test_refresh_date_serializes_correctly(self):
        """
        Given a fake `CoreTimeSeries` model object
        When the fake is passed to the `CoreTimeseriesSerializer`
        Then the `refresh_date` field is returned is the expected format
        """
        # Given
        fake_core_times_series = self._setup_fake_times_series()

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=fake_core_times_series)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        expected_date_value = str(fake_core_times_series.refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_date_serializes_correctly(self):
        """
        Given a fake `CoreTimeSeries` model object
        When the fake is passed to the `CoreTimeseriesSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        fake_core_time_series = self._setup_fake_times_series()

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=fake_core_time_series)

        # Then
        serialized_date: str = serializer.data["embargo"]
        expected_date_value = str(fake_core_time_series.embargo)

        assert serialized_date == expected_date_value

    def test_null_embargo_date_serializes_correctly(self):
        """
        Given a fake `CoreTimeSeries` model object and a null embargo timestamp
        When the fake is passed to the `CoreTimeseriesSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        fake_core_time_series = self._setup_fake_times_series()
        fake_core_time_series.embargo = None

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=fake_core_time_series)

        # Then
        serialized_date: str = serializer.data["embargo"]
        assert serialized_date == ""

    @pytest.mark.parametrize(
        "expected_field",
        [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "age",
            "stratum",
            "sex",
            "year",
            "date",
            "metric_value",
            "in_reporting_delay_period",
            "embargo",
            "metric_frequency",
            "refresh_date",
            "force_write",
        ],
    )
    def test_expected_fields_are_returned(self, expected_field: str):
        """
        Given a fake `CoreTimeseries` model object
        When the object is passed through the `CoreTimeSeriesSerializer`
        Then the expected fields are returned.
        """
        # Given
        fake_core_time_series = self._setup_fake_times_series()

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=fake_core_time_series)

        # Then
        assert expected_field in serializer.fields
