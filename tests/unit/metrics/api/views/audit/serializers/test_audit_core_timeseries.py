import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.data.models.core_models import CoreTimeSeries
from metrics.api.views.audit.serializers import AuditCoreTimeseriesSerializer

from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)


@pytest.fixture
def mock_core_times_series() -> mock.MagicMock:
    return mock.MagicMock(
        spec=CoreTimeSeries,
        metric__topic__sub_theme__theme__name="infectious_disease",
        metric__topic__sub_theme__name="respiratory",
        metric_topic="COVID-19",
        metric__name="COVID-19_cases_rateRollingMean",
        geography__name="England",
        geography__geography_type__name="Nation",
        stratum__name="default",
        age__name="all",
        sex="all",
        year=2024,
        date=datetime.date(day=1, month=1, year=2024),
        metric_value=Decimal("1.000"),
        refresh_date=datetime.datetime(day=1, month=1, year=2024),
        embargo=datetime.datetime(day=2, month=2, year=2024),
    )


class TestCoreTimeSeriesSerializer:

    def test_refresh_date_serializes_correctly(
        self,
        mock_core_times_series: mock.MagicMock,
    ):
        """
        Given a mocked `CoreTimeSeries` model object
        When the mock is passed to the `CoreTimeseriesSerializer`
        Then the `refresh_date` field is returned in the expected format.
        """
        # Given
        mocked_core_times_series = mock_core_times_series

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=mocked_core_times_series)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        expected_date_value = str(mocked_core_times_series.refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_date_serializes_correctly(
        self,
        mock_core_times_series: mock.MagicMock,
    ):
        """
        Given a mocked `CoreTimeSeries` model object
        When the mock is passed to the `CoreTimeseriesSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        mocked_core_times_series = mock_core_times_series

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=mocked_core_times_series)

        # Then
        serialized_date: str = serializer.data["embargo"]
        expected_date_value = str(mocked_core_times_series.embargo)

        assert serialized_date == expected_date_value

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
    def test_expected_fields_are_returned(
        self, expected_field: str, mock_core_times_series: mock.MagicMock
    ):
        """
        Given a mocked `CoreTimeseries` model object
        When the object is passed through the `CoreTimeSeriesSerializer`
        Then the expected fields are returned.
        """
        # Given
        mocked_core_timeseries = mock_core_times_series

        # When
        serializer = AuditCoreTimeseriesSerializer(instance=mocked_core_timeseries)

        # Then
        assert expected_field in serializer.fields
