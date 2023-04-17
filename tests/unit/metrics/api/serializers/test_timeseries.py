from metrics.api.serializers import APITimeSeriesSerializer
from tests.fakes.factories.api_time_series_factory import FakeAPITimeSeriesFactory
from tests.fakes.models.api_time_series import FakeAPITimeSeries


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
        serialized_dt: str = serializer.data["dt"]
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
