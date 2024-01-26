import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.api.serializers import CoreTimeSeriesSerializer
from metrics.data.models.core_models.timeseries import CoreTimeSeries


@pytest.fixture
def mock_core_times_series() -> mock.MagicMock:
    return mock.MagicMock(
        spec=CoreTimeSeries,
        metric__topic__sub_theme__theme__name="infectious_disease",
        metric__topic__sub_theme__name="respiratory",
        metric__topic__name="COVID-19",
        metric__name="COVID-19_cases_rateRollingMean",
        geography__name="England",
        geography__geography_type__name="Nation",
        stratum__name="default",
        age__name="all",
        sex="all",
        year=2024,
        date=datetime.date(day=1, month=1, year=2024),
        metric_value=Decimal("1.000"),
    )


class TestCoreTimeSeriesSerializer:
    def test_date_is_serialized_correctly(self, mock_core_times_series: mock.MagicMock):
        """
        Given a mocked `CoreTimesSeries` model object
        When the mock is passed to the `CoreTimeSeriesSerializer`
        Then the `date` field is returned in the expected format
        """
        # Given
        example_date = datetime.datetime(day=3, month=8, year=2023).date()
        mocked_core_time_series = mock_core_times_series
        mocked_core_time_series.date = example_date

        # When
        serializer = CoreTimeSeriesSerializer(instance=mocked_core_time_series)

        # Then
        serialized_date: str = serializer.data["date"]
        expected_date_value = str(mocked_core_time_series.date)
        # Instead of a datetime object, the string representation is expected to be returned by the serializer
        # i.e. '2023-03-08` instead of `datetime.date(year=2023, month=3, day=8)`
        assert serialized_date == expected_date_value

    def test_metric_value_is_serialized_correctly(
        self, mock_core_times_series: mock.MagicMock
    ):
        """
        Given a mocked `CoreTimesSeries` model object
        When the mock is passed to the `CoreTimeSeriesSerializer`
        Then the `metric_value` field is returned in the expected format
        """
        # Given
        example_metric_value = Decimal("1.9000")
        mocked_core_time_series = mock_core_times_series
        mocked_core_time_series.metric_value = example_metric_value

        # When
        serializer = CoreTimeSeriesSerializer(instance=mocked_core_time_series)

        # Then
        serialized_date: str = serializer.data["metric_value"]
        expected_date_value = str(mocked_core_time_series.metric_value)
        # Instead of a Decimal object, the string representation is expected to be returned by the serializer
        # i.e. '1.9000' instead of 'Decimal(1.9000)`
        assert serialized_date == expected_date_value

    @pytest.mark.parametrize(
        "related_field_name, serialized_field_name",
        (
            [
                ("metric__topic__sub_theme__theme__name", "theme"),
                ("metric__topic__sub_theme__name", "sub_theme"),
                ("metric__topic__name", "topic"),
                ("metric__name", "metric"),
                ("geography__name", "geography"),
                ("geography__geography_type__name", "geography_type"),
                ("stratum__name", "stratum"),
                ("age__name", "age"),
            ]
        ),
    )
    def test_related_fields_map_to_the_correct_serialized_fields(
        self,
        related_field_name: str,
        serialized_field_name: str,
        mock_core_times_series: mock.MagicMock,
    ):
        """
        Given a mocked `CoreTimesSeries` model object
        When the mock is passed to the `CoreTimeSeriesSerializer`
        Then related fields from other models are mapped to the correct serialized fields
        """
        # Given
        mocked_core_time_series = mock_core_times_series

        # When
        serializer = CoreTimeSeriesSerializer(instance=mocked_core_time_series)

        # Then
        serialized_field_value = serializer.data[serialized_field_name]
        model_object_value = str(getattr(mocked_core_time_series, related_field_name))
        assert serialized_field_value == model_object_value

    @pytest.mark.parametrize(
        "expected_field",
        [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "year",
            "date",
            "metric_value",
        ],
    )
    def test_expected_fields_are_returned(
        self, expected_field: str, mock_core_times_series: mock.MagicMock
    ):
        """
        Given a mocked `CoreTimesSeries` model object
        When the object is passed through the `CoreTimesSeriesSerializer`
        Then the expected fields are returned.
        """
        # Given
        mocked_core_time_series = mock_core_times_series

        # When
        serializer = CoreTimeSeriesSerializer(instance=mocked_core_time_series)

        # Then
        assert expected_field in serializer.fields
