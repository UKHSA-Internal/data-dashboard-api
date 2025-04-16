import datetime
from decimal import Decimal
from unittest import mock

import pytest

from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.managers.topic_manager import FakeTopicManager
from tests.fakes.models.metrics.topic import FakeTopic

from metrics.data.models.api_models import APITimeSeries
from metrics.api.views.audit.serializers import AuditAPITimeSeriesSerializer

from tests.fakes.factories.metrics.api_time_series_factory import (
    FakeAPITimeSeriesFactory,
)


class TestAPITimeseriesSerializer:

    def test_metric_value_is_serialized_correctly(self):
        """
        Given a fake `APITimeseries` model object
        When the fake is passed to the `AuditCoreHeadlineSerializer`
        Then the `metric_value` field is returned in the expected format.
        """
        # Given
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )
        fake_api_time_series_metric_value = fake_api_time_series.metric_value

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_metric_value: str = serializer.data["metric_value"]
        expected_metric_value = float(fake_api_time_series_metric_value)

        assert serialized_metric_value == expected_metric_value

    def test_refresh_date_is_serialized_correctly(self):
        """
        Given a fake `APITimeSeries` model object
        When the fake is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )
        fake_api_time_series_refresh_date = fake_api_time_series.refresh_date

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        expected_date_value = str(fake_api_time_series_refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_date_is_serialized_correctly(self):
        """
        Given a fake `APITimeSeries` model object
        When the fake is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )
        fake_api_time_series_embargo = fake_api_time_series.embargo

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_date: str = serializer.data["embargo"]
        expected_date_value = str(fake_api_time_series_embargo)

        assert serialized_date == expected_date_value

    def test_null_embargo_date_is_serialized_correctly(self):
        """
        Given a fake `APITimeSeries` model object
        When the fake is passed to the `APITimeseriesSerializer`
        Then the `embargo` field is returned in the expected format
        """
        # Given
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )
        fake_api_time_series.embargo = None

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_date: str = serializer.data["embargo"]

        assert serialized_date == ""

    @pytest.mark.parametrize(
        "expected_field",
        [
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography",
            "geography_type",
            "stratum",
            "age",
            "sex",
        ],
    )
    def test_serializer_returns_expected_fields(
        self,
        expected_field: str,
    ):
        """
        Given a fake `APITimeSeries` model object
        When the fake is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_field = serializer.data[expected_field]
        model_object_field = str(getattr(fake_api_time_series, expected_field))

        assert serialized_field == model_object_field
