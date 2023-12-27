import datetime
import pytest

from metrics.api.serializers import CoreTimeSeriesSerializer
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class TestCoreTimeSeriesSerializer:
    def test_date_is_serialized_correctly(self):
        """
        Given an `CoreTimeSeries` instance
        When that instance is passed through the `CoreTimeSeriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        example_date = datetime.datetime(day=3, month=8, year=2023).date()
        fake_core_time_series: FakeAPITimeSeries = (
            FakeCoreTimeSeriesFactory.build_time_series(
                date=example_date,
                metric_name="COVID-19_cases_rateRollingMean",
                topic_name="COVID-19",
            )
        )

        # When
        serializer = CoreTimeSeriesSerializer(instance=fake_core_time_series)

        # Then
        serialized_date: str = serializer.data["date"]
        expected_date_value = str(fake_core_time_series.date)
        # Instead of a datetime object, the string representation is expected to be returned by the serializer
        # i.e. '2023-03-08` instead of `datetime.date(year=2023, month=3, day=8)`
        assert serialized_date == expected_date_value

    def test_metric_value_is_serialized_correctly(self):
        """
        Given an `CoreTimeSeries` instance
        When that instance is passed through the `CoreTimeSeriesSerializer`
        Then the `metric_value` field is returned correctly
        """
        # Given
        metric_value = 123
        fake_core_time_series: FakeAPITimeSeries = (
            FakeCoreTimeSeriesFactory.build_time_series(
                date=datetime.datetime(day=3, month=8, year=2023).date(),
                metric_name="COVID-19_cases_rateRollingMean",
                topic_name="COVID-19",
                metric_value=metric_value,
            )
        )

        # When
        serializer = CoreTimeSeriesSerializer(instance=fake_core_time_series)

        # Then
        serialized_metric_value: float = serializer.data["metric_value"]
        expected_metric_value = fake_core_time_series.metric_value
        assert serialized_metric_value == f"{expected_metric_value:.4f}"

    @pytest.mark.parametrize(
        "expected_field",
        [
            "id",
            "metric_frequency",
            "sex",
            "year",
            "month",
            "epiweek",
            "refresh_date",
            "embargo",
            "geography",
            "stratum",
            "age",
        ],
    )
    def test_fields_are_serialized_correctly(self, expected_field: str):
        """
        Given an `CoreTimeSeries` instance
        When that instance is passed through the `CoreTimeSeriesSerializer`
        Then the returned fields match the ones from the input model instance
        """
        # Given
        fake_core_time_series: FakeAPITimeSeries = (
            FakeCoreTimeSeriesFactory.build_time_series(
                date=datetime.datetime(day=3, month=8, year=2023).date(),
                metric_name="COVID-19_cases_rateRollingMean",
                topic_name="COVID-19",
            )
        )
        # When
        serializer = CoreTimeSeriesSerializer(instance=fake_core_time_series)

        # Then
        serialized_field_value = serializer.data[expected_field]
        value_on_model = getattr(fake_core_time_series, expected_field)
        assert serialized_field_value == value_on_model
