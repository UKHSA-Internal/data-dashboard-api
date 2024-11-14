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


@pytest.fixture
def mock_api_time_series() -> mock.MagicMock:
    return mock.MagicMock(
        spec=APITimeSeries,
        theme="infectious_disease",
        sub_theme="respiratory",
        topic="COVID-19",
        metric="COVID-19_cases_rateRollingMean",
        geography="England",
        geography_type="Nation",
        stratum="default",
        age="all",
        sex="all",
        period_start=datetime.datetime(day=1, month=1, year=2024),
        period_end=datetime.datetime(day=2, month=2, year=2024),
        metric_value=Decimal("1.000"),
        refresh_date=datetime.datetime(day=1, month=1, year=2024),
        embargo=datetime.datetime(day=2, month=2, year=2024),
    )


class TestAPITimeseriesSerializer:

    def test_metric_value_is_serialized_correctly(
        self, mock_api_time_series: mock.MagicMock
    ):
        """
        Given a mocked `APITimeseries` model object
        When the mock is passed to the `AuditCoreHeadlineSerializer`
        Then the `metric_value` field is returned in the expected format.
        """
        # Given
        example_metric_value = Decimal("1.9000")
        mocked_api_time_series = mock_api_time_series
        mocked_api_time_series.metric_value = example_metric_value

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=mocked_api_time_series)

        # Then
        serialized_metric_value: str = serializer.data["metric_value"]
        expected_metric_value = float(mocked_api_time_series.metric_value)

        assert serialized_metric_value == expected_metric_value

    def test_refresh_date_is_serialized_correctly(
        self, mock_api_time_series: mock.MagicMock
    ):
        """
        Given a mocked `APITimeSeries` model object
        When the mock is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        mocked_api_time_series = mock_api_time_series

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=mocked_api_time_series)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        expected_date_value = str(mocked_api_time_series.refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_date_is_serialized_correctly(
        self, mock_api_time_series: mock.MagicMock
    ):
        """
        Given a mocked `APITimeSeries` model object
        When the mock is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        mocked_api_time_series = mock_api_time_series

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=mocked_api_time_series)

        # Then
        serialized_date: str = serializer.data["embargo"]
        expected_date_value = str(mocked_api_time_series.embargo)

        assert serialized_date == expected_date_value

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
        mock_api_time_series: mock.MagicMock,
        expected_field: str,
    ):
        """
        Given a mocked `APITimeSeries` model object
        When the mock is passed to the `APITimeseriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        mocked_api_time_series = mock_api_time_series

        # When
        serializer = AuditAPITimeSeriesSerializer(instance=mocked_api_time_series)

        # Then
        serialized_field = serializer.data[expected_field]
        model_object_field = str(getattr(mocked_api_time_series, expected_field))

        assert serialized_field == model_object_field
