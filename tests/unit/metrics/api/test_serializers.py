import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers import APITimeSeriesSerializer, ChartsQuerySerializer
from tests.fakes.models.fake_api_time_series import FakeAPITimeSeries
from tests.fakes.models.fake_api_time_series_factory import FakeAPITimeSeriesFactory


class TestAPITimeSeriesSerializer:
    def test_dt_is_serialized_correctly(self):
        """
        Given an `APITimeSeries` instance
        When that instance is passed through the `APITimeSeriesSerializer`
        Then the `dt` field is returned in the expected format
        """
        # Given
        fake_api_time_series: FakeAPITimeSeries = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )

        # When
        serializer = APITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_dt = serializer.data["dt"]
        expected_dt_value = str(fake_api_time_series.dt)
        # Instead of a datetime object, the string representation is expected to be returned by the serializer
        # i.e. '2023-03-08` instead of `datetime.date(year=2023, month=3, day=8)`
        assert serialized_dt == expected_dt_value

    def test_data_is_serialized_correctly(self):
        """
        Given an `APITimeSeries` instance
        When that instance is passed through the `APITimeSeriesSerializer`
        Then the returned fields match the ones from the input model instance
        """
        # Given
        fake_api_time_series: FakeAPITimeSeries = (
            FakeAPITimeSeriesFactory.build_example_covid_time_series()
        )

        # When
        serializer = APITimeSeriesSerializer(instance=fake_api_time_series)

        # Then
        serialized_data = serializer.data
        serialized_data.pop("dt")
        # Datetime stamp is tested separately
        # because the str representation is serialized differently to other types

        for serialized_field_name, serialized_field_value in serialized_data.items():
            value_on_model = getattr(fake_api_time_series, serialized_field_name)
            assert serialized_field_value == value_on_model


class TestChartsQuerySerializer:
    @pytest.mark.parametrize("file_format", ["svg", "png", "jpg", "jpeg"])
    def test_valid_file_format(self, file_format: str):
        """
        Given a valid file format passed to a `ChartsQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        data = {"file_format": file_format}
        serializer = ChartsQuerySerializer(data=data)

        # When
        is_serializer_valid: bool = serializer.is_valid()

        # Then
        assert is_serializer_valid

    def test_invalid_file_format(self):
        """
        Given an invalid file format passed to a `ChartsQuerySerializer` object
        When `is_valid(raise_exception=True)` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        data = {"file_format": "invalid.file.format"}
        serializer = ChartsQuerySerializer(data=data)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
