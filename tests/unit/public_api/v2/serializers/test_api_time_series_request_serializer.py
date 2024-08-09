from unittest import mock

import pytest

from metrics.data.models.api_models import APITimeSeries
from public_api.serializers.api_time_series_request_serializer import (
    NO_LOOKUP_FIELD_ERROR_MESSAGE,
    APITimeSeriesDTO,
)

from public_api.v2.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializerV2,
)

from tests.fakes.factories.metrics.api_time_series_factory import (
    FakeAPITimeSeriesFactory,
)
from tests.fakes.managers.api_time_series_manager import FakeAPITimeSeriesManager
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class TestAPITimeSeriesRequestSerializerV2:
    @staticmethod
    def _setup_fake_api_time_series() -> list[FakeAPITimeSeries]:
        # Multiple `APITimeSeries` objects with 2 distinct `theme` values
        return [
            # distinct theme value - `infectious_disease`
            FakeAPITimeSeriesFactory.build_example_covid_time_series(),
            FakeAPITimeSeriesFactory.build_example_covid_time_series(),
            # distinct theme value - `genetic_disease`
            FakeAPITimeSeriesFactory.build_example_sickle_cell_disease_series(),
        ]

    def test_lookup_field_gets_field_from_context(self):
        """
        Given a context dict which contains a `lookup_field` key-value pair
        When the `lookup_field` property is accessed from an instance of the `APITimeSeriesRequestSerializer`
        Then the value of the `lookup_field` key-value pair is returned
        """
        # Given
        lookup_field = "test_lookup_field"
        context_with_lookup_field = {"lookup_field": lookup_field}
        serializer = APITimeSeriesRequestSerializerV2(context=context_with_lookup_field)

        # When
        returned_lookup_field = serializer.lookup_field

        # Then
        assert returned_lookup_field == lookup_field

    def test_lookup_field_raises_error_when_lookup_field_not_found(self):
        """
        Given a context dict which does not contain a `lookup_field` key-value pair
        When the `lookup_field` property is accessed from an instance of the `APITimeSeriesRequestSerializer`
        Then a `NotImplementedError` is raised
        """
        # Given
        context_without_lookup_field = {}
        serializer = APITimeSeriesRequestSerializerV2(
            context=context_without_lookup_field
        )

        # When / Then
        with pytest.raises(NotImplementedError, match=NO_LOOKUP_FIELD_ERROR_MESSAGE):
            serializer.lookup_field

    def test_get_formatted_kwargs_from_request(self):
        """
        Given a request which contains kwargs from the URL parameters
        When `get_formatted_kwargs_from_request()` is called from an instance of the `APITimeSeriesRequestSerializer`
        Then the kwargs from the request URL parameters are returned and any + symbols replaced with spaces.
        """
        # Given
        fake_request_kwargs = {
            "theme": "infectious_disease",
            "geography_type": "Government+Office+Region",
        }
        fake_parser_context = {"kwargs": fake_request_kwargs}
        mocked_request = mock.Mock(parser_context=fake_parser_context)
        serializer = APITimeSeriesRequestSerializerV2(
            context={"request": mocked_request}
        )

        # When
        expected_request_kwargs = {
            "theme": "infectious_disease",
            "geography_type": "Government Office Region",
        }
        returned_kwargs_from_request = serializer.get_formatted_kwargs_from_request()

        # Then
        assert returned_kwargs_from_request == expected_request_kwargs

    def test_get_timeseries_dto_slice_returns_list_of_dto_objects_for_topic_lookup(
        self,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And a `lookup_field` of `topic` also provided in the context of the serializer
        When `get_timeseries_dto_slice()` is called from an instance of the `APITimeSeriesRequestSerializer`
        Then a list of distinct `APITimeSeriesDTO` objects are returned with the correct fields set on them
        """
        fake_request_kwargs = {
            "theme": "infectious_disease",
            "sub_theme": "respiratory",
        }
        fake_lookup_field = "topic"
        mocked_request = mock.Mock(parser_context={"kwargs": fake_request_kwargs})

        fake_api_timeseries_manager = FakeAPITimeSeriesManager(
            time_series=self._setup_fake_api_time_series()
        )

        serializer = APITimeSeriesRequestSerializerV2(
            context={
                "request": mocked_request,
                "lookup_field": fake_lookup_field,
                "api_time_series_manager": fake_api_timeseries_manager,
            }
        )

        # When
        timeseries_dto_slice: list[APITimeSeriesDTO] = (
            serializer.build_timeseries_dto_slice()
        )

        # Then
        serialized_api_timeseries_dto = timeseries_dto_slice[0]
        assert serialized_api_timeseries_dto.theme == "infectious_disease"
        assert serialized_api_timeseries_dto.sub_theme == "respiratory"
        assert (
            serialized_api_timeseries_dto.topic
            == serialized_api_timeseries_dto.name
            == "COVID-19"
        )

        assert not serialized_api_timeseries_dto.information
        assert not serialized_api_timeseries_dto.geography_type
        assert not serialized_api_timeseries_dto.geography
        assert not serialized_api_timeseries_dto.metric
