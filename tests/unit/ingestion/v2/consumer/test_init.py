from unittest import mock

from ingestion.utils import type_hints
from ingestion.v2.consumer import Consumer

MODULE_PATH = "ingestion.v2.consumer"


class TestConsumerInit:
    @mock.patch(f"{MODULE_PATH}.build_headline_dto_from_source")
    def test_build_dto_delegates_call_to_build_headline_dto_from_source(
        self,
        spy_build_headline_dto_from_source: mock.MagicMock,
        example_headline_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given headline type source data
        When a `Consumer` object is created
        Then a DTO is created by calling out
            to `build_headline_dto_from_source()`

        Patches:
            `spy_build_headline_dto_from_source`: To check
                the `HeadlineDTO` is created

        """
        # Given
        fake_data = example_headline_data

        # When
        consumer = Consumer(source_data=fake_data)
        dto = consumer.dto

        # Then
        spy_build_headline_dto_from_source.assert_called_once_with(
            source_data=fake_data
        )
        assert dto == spy_build_headline_dto_from_source.return_value

    @mock.patch(f"{MODULE_PATH}.build_time_series_dto_from_source")
    def test_build_dto_delegates_call_to_build_time_series_dto_from_source(
        self,
        spy_build_time_series_dto_from_source: mock.MagicMock,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given time series type source data
        When a `Consumer` object is created
        Then a DTO is created by calling out
            to `build_time_series_dto_from_source()`

        Patches:
            `spy_build_time_series_dto_from_source`: To check
                the `HeadlineDTO` is created

        """
        # Given
        fake_data = example_time_series_data

        # When
        consumer = Consumer(source_data=fake_data)
        dto = consumer.dto

        # Then
        spy_build_time_series_dto_from_source.assert_called_once_with(
            source_data=fake_data
        )
        assert dto == spy_build_time_series_dto_from_source.return_value
