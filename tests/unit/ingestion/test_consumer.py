from unittest import mock

import pytest
from django.db.models.manager import Manager

from ingestion.consumer import Consumer, FieldsAndModelManager
from ingestion.data_transfer_models import (
    IncomingHeadlineDTO,
    IncomingTimeSeriesDTO,
    OutgoingHeadlineDTO,
    OutgoingTimeSeriesDTO,
)
from ingestion.reader import Reader
from metrics.data.models import core_models

MODULE_PATH = "ingestion.consumer"


class TestConsumer:
    # Headline DTO construction tests

    @pytest.mark.parametrize(
        "field_on_incoming_headline_dto, field_on_outgoing_headline_dto",
        (
            # Common fields for either DTO type
            ["parent_theme", "theme"],
            ["child_theme", "sub_theme"],
            ["topic", "topic"],
            ["metric_group", "metric_group"],
            ["metric", "metric"],
            ["geography_type", "geography_type"],
            ["geography", "geography"],
            ["age", "age"],
            ["sex", "sex"],
            ["stratum", "stratum"],
            ["refresh_date", "refresh_date"],
            ["embargo", "embargo"],
            ["metric_value", "metric_value"],
            # HeadlineDTO specific fields
            ["period_start", "period_start"],
            ["period_end", "period_end"],
        ),
    )
    def test_to_outgoing_headline_dto(
        self,
        field_on_incoming_headline_dto: str,
        field_on_outgoing_headline_dto: str,
        example_incoming_headline_dto: IncomingHeadlineDTO,
    ):
        """
        Given an enriched `IncomingHeadlineDTO` instance
        When `to_outgoing_headline_dto()` is called
            from an instance of `Consumer`
        Then the returned `OutgoingHeadlineDTO` is enriched
            with the correct fields
        """
        # Given
        consumer = Consumer(data=mock.Mock())

        # When
        returned_outgoing_headline_dto: OutgoingHeadlineDTO = (
            consumer.to_outgoing_headline_dto(
                incoming_headline_dto=example_incoming_headline_dto
            )
        )

        # Then
        field_value_from_incoming_dto = getattr(
            example_incoming_headline_dto, field_on_incoming_headline_dto
        )
        field_value_from_outgoing_dto = getattr(
            returned_outgoing_headline_dto, field_on_outgoing_headline_dto
        )
        assert field_value_from_outgoing_dto == field_value_from_incoming_dto

    @mock.patch.object(Consumer, "to_outgoing_headline_dto")
    def test_convert_to_outgoing_headline_dtos(
        self, spy_to_outgoing_headline_dto: mock.MagicMock
    ):
        """
        Given a list of mocked `IncomingHeadlineDTO` instances
        When `_convert_to_outgoing_headline_dtos()` is called
            from an instance of `Consumer`
        Then the call is delegated to the `to_outgoing_headline_dto()`
            method for each `IncomingHeadlineDTO` instance

        Patches:
            `spy_to_outgoing_headline_dto`: For the main assertion.
                To check each `OutgoingHeadlineDTO` is built via
                calls to `to_outgoing_headline_dto()`

        """
        # Given
        mocked_raw_headline_one = mock.Mock()
        mocked_raw_headline_two = mock.Mock()
        mocked_incoming_headline_dtos = [
            mocked_raw_headline_one,
            mocked_raw_headline_two,
        ]
        consumer = Consumer(data=mock.Mock())

        # When
        converted_headline_dtos = consumer._convert_to_outgoing_headline_dtos(
            processed_headline_dtos=mocked_incoming_headline_dtos
        )

        # Then
        expected_calls = [
            mock.call(incoming_headline_dto=mocked_raw_headline_one),
            mock.call(incoming_headline_dto=mocked_raw_headline_two),
        ]
        spy_to_outgoing_headline_dto.assert_has_calls(expected_calls, any_order=True)

        assert (
            converted_headline_dtos == [spy_to_outgoing_headline_dto.return_value] * 2
        )

    # Timeseries DTO construction tests

    @pytest.mark.parametrize(
        "field_on_incoming_timeseries_dto, field_on_outgoing_timeseries_dto",
        (
            # Common fields for either DTO type
            ["parent_theme", "theme"],
            ["child_theme", "sub_theme"],
            ["topic", "topic"],
            ["metric_group", "metric_group"],
            ["metric", "metric"],
            ["geography_type", "geography_type"],
            ["geography", "geography"],
            ["age", "age"],
            ["sex", "sex"],
            ["stratum", "stratum"],
            ["refresh_date", "refresh_date"],
            ["embargo", "embargo"],
            ["metric_value", "metric_value"],
            # TimeSeriesDTO specific fields
            ["metric_frequency", "metric_frequency"],
            ["year", "year"],
            ["month", "month"],
            ["epiweek", "epiweek"],
            ["date", "date"],
        ),
    )
    def test_to_outgoing_timeseries_dto(
        self,
        field_on_incoming_timeseries_dto: str,
        field_on_outgoing_timeseries_dto: str,
        example_incoming_timeseries_dto: IncomingTimeSeriesDTO,
    ):
        """
        Given an enriched `IncomingTimeSeriesDTO` instance
        When `to_outgoing_timeseries_dto()` is called
            from an instance of `Consumer`
        Then the returned `OutgoingHeadlineDTO` is enriched
            with the correct fields
        """
        # Given
        consumer = Consumer(data=mock.Mock())

        # When
        returned_outgoing_timseries_dto: OutgoingTimeSeriesDTO = (
            consumer.to_outgoing_timeseries_dto(
                incoming_timeseries_dto=example_incoming_timeseries_dto
            )
        )

        # Then
        field_value_from_incoming_dto = getattr(
            example_incoming_timeseries_dto, field_on_incoming_timeseries_dto
        )
        field_value_from_outgoing_dto = getattr(
            returned_outgoing_timseries_dto, field_on_outgoing_timeseries_dto
        )
        assert field_value_from_outgoing_dto == field_value_from_incoming_dto

    @mock.patch.object(Consumer, "to_outgoing_timeseries_dto")
    def test_convert_to_outgoing_timeseries_dtos(
        self, spy_to_outgoing_timeseries_dto: mock.MagicMock
    ):
        """
        Given a list of mocked `IncomingTimeseriesDTO` instances
        When `_convert_to_outgoing_timeseries_dtos()` is called
            from an instance of `Consumer`
        Then the call is delegated to the `to_outgoing_timeseries_dto()`
            method for each `IncomingTimeseriesDTO` instance

        Patches:
            `spy_to_outgoing_timeseries_dto`: For the main assertion.
                To check each `OutgoingTimeSeriesDTO` is built via
                calls to `to_outgoing_timeseries_dto()`

        """
        # Given
        mocked_raw_timeseries_one = mock.Mock()
        mocked_raw_timeseries_two = mock.Mock()
        mocked_incoming_timeseries_dtos = [
            mocked_raw_timeseries_one,
            mocked_raw_timeseries_two,
        ]
        consumer = Consumer(data=mock.Mock())

        # When
        converted_timeseries_dtos = consumer._convert_to_outgoing_timeseries_dtos(
            processed_timeseries_dtos=mocked_incoming_timeseries_dtos
        )

        # Then
        expected_calls = [
            mock.call(incoming_timeseries_dto=mocked_raw_timeseries_one),
            mock.call(incoming_timeseries_dto=mocked_raw_timeseries_two),
        ]
        spy_to_outgoing_timeseries_dto.assert_has_calls(expected_calls, any_order=True)

        assert (
            converted_timeseries_dtos
            == [spy_to_outgoing_timeseries_dto.return_value] * 2
        )

    @pytest.mark.parametrize(
        "attribute_on_class, expected_model_manager",
        [
            ("theme_manager", core_models.Theme.objects),
            ("sub_theme_manager", core_models.SubTheme.objects),
            ("topic_manager", core_models.Topic.objects),
            ("metric_group_manager", core_models.MetricGroup.objects),
            ("metric_manager", core_models.Metric.objects),
            ("geography_type_manager", core_models.GeographyType.objects),
            ("geography_manager", core_models.Geography.objects),
            ("age_manager", core_models.Age.objects),
            ("stratum_manager", core_models.Stratum.objects),
            ("core_headline_manager", core_models.CoreHeadline.objects),
            ("core_timeseries_manager", core_models.CoreTimeSeries.objects),
        ],
    )
    def test_initializes_with_default_core_model_managers(
        self, attribute_on_class: str, expected_model_manager: Manager
    ):
        """
        Given an instance of `Consumer`
        When the object is initialized
        Then the concrete core model managers
            are set on the `Consumer` object
        """
        # Given
        mocked_data = mock.Mock()

        # When
        consumer = Consumer(data=mocked_data)

        # Then
        assert getattr(consumer, attribute_on_class) == expected_model_manager

    def test_initializes_with_default_reader(self):
        """
        Given an instance of `Consumer`
        When the object is initialized
        Then a `Reader` object is set on the `Consumer` object
        """
        # Given
        mocked_data = mock.Mock()

        # When
        consumer = Consumer(data=mocked_data)

        # Then
        assert type(consumer.reader) is Reader
        assert consumer.reader.data == mocked_data

    @mock.patch.object(Consumer, "create_outgoing_headlines_dtos_from_source")
    @mock.patch(f"{MODULE_PATH}.create_core_headlines")
    def test_create_headlines_delegates_call_correctly(
        self,
        spy_create_core_headlines: mock.MagicMock,
        spy_create_outgoing_headlines_dtos_from_source: mock.MagicMock,
    ):
        """
        Given mocked data
        When `create_headlines()` is called from an instance of `Consumer`
        Then the call is delegated to `create_core_headlines()`
        """
        # Given
        mocked_core_headline_manager = mock.Mock()
        consumer = Consumer(
            data=mock.Mock(),
            reader=mock.Mock(),  # Stubbed
            core_headline_manager=mocked_core_headline_manager,
        )
        batch_size = 100

        # When
        consumer.create_headlines()

        # Then
        expected_outgoing_headline_dtos = (
            spy_create_outgoing_headlines_dtos_from_source.return_value
        )
        spy_create_core_headlines.assert_called_once_with(
            headline_dtos=expected_outgoing_headline_dtos,
            core_headline_manager=mocked_core_headline_manager,
            batch_size=batch_size,
        )

    @mock.patch.object(Consumer, "create_outgoing_timeseries_dtos_from_source")
    @mock.patch(f"{MODULE_PATH}.create_core_and_api_timeseries")
    def test_create_timeseries_delegates_call_correctly(
        self,
        spy_create_core_and_api_timeseries: mock.MagicMock,
        spy_create_outgoing_timeseries_dtos_from_source: mock.MagicMock,
    ):
        """
        Given mocked data
        When `create_timeseries()` is called from an instance of `Consumer`
        Then the call is delegated to `create_core_and_api_timeseries()`
        """
        # Given
        mocked_core_timeseries_manager = mock.Mock()
        consumer = Consumer(
            data=mock.Mock(),
            reader=mock.Mock(),  # Stubbed
            core_timeseries_manager=mocked_core_timeseries_manager,
        )
        batch_size = 100

        # When
        consumer.create_timeseries()

        # Then
        expected_outgoing_timeseries_dtos = (
            spy_create_outgoing_timeseries_dtos_from_source.return_value
        )
        spy_create_core_and_api_timeseries.assert_called_once_with(
            timeseries_dtos=expected_outgoing_timeseries_dtos,
            core_time_series_manager=mocked_core_timeseries_manager,
            batch_size=batch_size,
        )

    @pytest.mark.parametrize(
        "expected_index, expected_fields, expected_model_manager_from_class",
        [
            (0, {"parent_theme": "name"}, "theme_manager"),
            (
                1,
                {"child_theme": "name", "parent_theme": "theme_id"},
                "sub_theme_manager",
            ),
            (2, {"topic": "name", "child_theme": "sub_theme_id"}, "topic_manager"),
            (3, {"geography_type": "name"}, "geography_type_manager"),
            (
                4,
                {
                    "geography": "name",
                    "geography_type": "geography_type_id",
                    "geography_code": "geography_code",
                },
                "geography_manager",
            ),
            (5, {"metric_group": "name", "topic": "topic_id"}, "metric_group_manager"),
            (
                6,
                {
                    "metric": "name",
                    "metric_group": "metric_group_id",
                    "topic": "topic_id",
                },
                "metric_manager",
            ),
            (7, {"stratum": "name"}, "stratum_manager"),
            (8, {"age": "name"}, "age_manager"),
        ],
    )
    def test_get_all_related_fields_and_model_managers(
        self,
        expected_index: int,
        expected_fields: dict[str, str],
        expected_model_manager_from_class: str,
    ):
        """
        Given mocked data
        When `get_all_related_fields_and_model_managers()` is called
            from an instance of `Consumer`
        Then the correct list of named tuples is returned
            where each named tuple contains the
            relevant fields and the corresponding model manager
        """
        # Given
        mocked_data = mock.Mock()
        consumer = Consumer(data=mocked_data)

        # When
        all_related_fields_and_model_managers: list[
            FieldsAndModelManager
        ] = consumer.get_all_related_fields_and_model_managers()

        # Then
        assert (
            all_related_fields_and_model_managers[expected_index].fields
            == expected_fields
        )
        assert all_related_fields_and_model_managers[
            expected_index
        ].model_manager == getattr(consumer, expected_model_manager_from_class)

    def test_create_incoming_headline_dtos_from_source(
        self, example_headline_data: list[dict[str, str | float]]
    ):
        """
        Given some sample headline data
        When `create_incoming_headline_dtos_from_source()`
            is called from an instance of `Consumer`
        Then a list of `IncomingHeadlineDTO`s are returned
        """
        # Given
        fake_incoming_headline_source_data = example_headline_data
        consumer = Consumer(data=mock.Mock())

        # When
        returned_incoming_headline_dtos = (
            consumer.create_incoming_headline_dtos_from_source(
                incoming_source_data=fake_incoming_headline_source_data,
            )
        )

        # Then
        expected_created_incoming_headline_dtos = [
            IncomingHeadlineDTO(**data) for data in fake_incoming_headline_source_data
        ]
        assert (
            returned_incoming_headline_dtos == expected_created_incoming_headline_dtos
        )

    def test_create_incoming_headline_dtos_from_source_filters_out_none_metric_values(
        self, example_headline_data: list[dict[str, str | float]]
    ):
        """
        Given some sample headline data with a metric value of None
        When `create_incoming_headline_dtos_from_source()`
            is called from an instance of `Consumer`
        Then a list of `IncomingHeadlineDTO`s are returned
        And the entry with a None "metric_value" is filtered out
        """
        # Given
        fake_example_data_with_metric_value = example_headline_data[0]
        fake_example_data_with_none_metric_value = example_headline_data[1]
        fake_example_data_with_none_metric_value["metric_value"] = None
        consumer = Consumer(data=mock.Mock())

        # When
        returned_incoming_headline_dtos = (
            consumer.create_incoming_headline_dtos_from_source(
                incoming_source_data=example_headline_data,
            )
        )

        # Then
        expected_created_incoming_headline_dtos = [
            IncomingHeadlineDTO(**fake_example_data_with_metric_value)
        ]
        assert (
            returned_incoming_headline_dtos == expected_created_incoming_headline_dtos
        )
        assert all(
            returned_dto.metric_value is not None
            for returned_dto in returned_incoming_headline_dtos
        )

    def test_create_incoming_timeseries_dtos_from_source(
        self, example_timeseries_data: list[dict[str, str | float]]
    ):
        """
        Given some sample timeseries data
        When `create_incoming_timeseries_dtos_from_source()`
            is called from an instance of `Consumer`
        Then a list of `IncomingTimeSeriesDTO`s are returned
        """
        # Given
        fake_incoming_timeseries_source_data = example_timeseries_data
        consumer = Consumer(data=mock.Mock())

        # When
        returned_incoming_timeseries_dtos = (
            consumer.create_incoming_timeseries_dtos_from_source(
                incoming_source_data=fake_incoming_timeseries_source_data,
            )
        )

        # Then
        expected_created_incoming_timeseries_dtos = [
            IncomingTimeSeriesDTO(**data)
            for data in fake_incoming_timeseries_source_data
        ]
        assert (
            returned_incoming_timeseries_dtos
            == expected_created_incoming_timeseries_dtos
        )

    def test_create_incoming_timeseries_dtos_from_source_filters_out_none_metric_values(
        self, example_timeseries_data: list[dict[str, str | float]]
    ):
        """
        Given some sample timeseries data with a metric value of None
        When `create_incoming_timeseries_dtos_from_source()`
            is called from an instance of `Consumer`
        Then a list of `IncomingTimeSeriesDTO`s are returned
        And the entry with a None "metric_value" is filtered out
        """
        # Given
        fake_example_data_with_metric_value = example_timeseries_data[0]
        fake_example_data_with_none_metric_value = example_timeseries_data[1]
        fake_example_data_with_none_metric_value["metric_value"] = None
        consumer = Consumer(data=mock.Mock())

        # When
        returned_incoming_timeseries_dtos = (
            consumer.create_incoming_timeseries_dtos_from_source(
                incoming_source_data=example_timeseries_data,
            )
        )

        # Then
        expected_created_incoming_timeseries_dtos = [
            IncomingTimeSeriesDTO(**fake_example_data_with_metric_value)
        ]
        assert (
            returned_incoming_timeseries_dtos
            == expected_created_incoming_timeseries_dtos
        )
        assert all(
            returned_dto.metric_value is not None
            for returned_dto in returned_incoming_timeseries_dtos
        )
