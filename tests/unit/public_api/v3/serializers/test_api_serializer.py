from unittest import mock
from django.db import models

import pytest

from public_api.version.v3.serializers.api_request_serializer import (
    NO_LOOKUP_FIELD_ERROR_MESSAGE,
    APIRequestSerializerv3,
)
from tests.fakes.factories.metrics.api_time_series_factory import (
    FakeAPITimeSeriesFactory,
)
from tests.fakes.managers.api_time_series_manager import FakeAPITimeSeriesManager
from tests.fakes.models.metrics.api_time_series import FakeAPITimeSeries


class TestAPITimeSeriesRequestSerializerV3:
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
        serializer = APIRequestSerializerv3(context=context_with_lookup_field)

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
        serializer = APIRequestSerializerv3(context=context_without_lookup_field)

        # When / Then
        with pytest.raises(NotImplementedError, match=NO_LOOKUP_FIELD_ERROR_MESSAGE):
            _ = serializer.lookup_field

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
        serializer = APIRequestSerializerv3(context={"request": mocked_request})

        # When
        expected_request_kwargs = {
            "theme": "infectious_disease",
            "geography_type": "Government Office Region",
        }
        returned_kwargs_from_request = serializer.get_formatted_kwargs_from_request()

        # Then
        assert returned_kwargs_from_request == expected_request_kwargs

    @pytest.mark.parametrize(
        "api_model",
        [
            MetricsPublicAPIInterface.get_api_timeseries_model(),
            MetricsPublicAPIInterface.get_api_headline_model(),
        ],
    )
    def test_get_queryset_does_not_use_permissions_without_authentication(
        self, api_model: models.Model
    ):
        # This isn't a scenario that could happen but tested anyway to prevent it
        # from creeping in
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }
        mocked_request = mock.Mock(
            auth=None,
            user=mock.Mock(permission_sets=permission_sets),
            parser_context={"kwargs": {}},
        )

        serializer = APIRequestSerializerv3(
            context={
                "request": mocked_request,
                "lookup_field": "theme",
                "api_model": api_model,
            }
        )

        with (
            mock.patch.object(api_model, "objects") as api_manager_spy,
            mock.patch(
                "public_api.auth.MetricsPublicAPIInterface.is_auth_enabled",
                return_value=True,
            ),
        ):
            serializer.get_queryset()

            api_manager_spy.get_distinct_column_values_with_filters.assert_called_once_with(
                lookup_field="theme",
                permission_sets=None,
            )

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

        serializer = APIRequestSerializerv3(
            context={
                "request": mocked_request,
                "lookup_field": fake_lookup_field,
                "api_model": mock.Mock(objects=fake_api_timeseries_manager),
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
