from unittest import mock

from ingestion.v2.consumer import ConsumerV2

MODULE_PATH = "ingestion.v2.consumer"


class TestConsumerCreateModelMethods:
    @mock.patch(f"{MODULE_PATH}.create_records")
    @mock.patch.object(ConsumerV2, "build_core_headlines")
    def test_create_core_headlines_delegates_calls_successfully(
        self,
        spy_build_core_headlines: mock.MagicMock,
        spy_create_records: mock.MagicMock,
    ):
        """
        Given an instance of the `Consumer`
        When `create_core_headlines()` is called from the object
        Then the `create_records()` function is called
            with the correct args

        Patches:
            `spy_build_core_headlines`: To check the
                `CoreHeadline` model instances are built
                and passed to `create_records()`
            `spy_create_records`: For the main assertion
        """
        # Given
        consumer = ConsumerV2(data=mock.Mock())

        # When
        consumer.create_core_headlines()

        # Then
        spy_build_core_headlines.assert_called_once()
        spy_create_records.assert_called_once_with(
            model_manager=consumer.core_headline_manager,
            model_instances=spy_build_core_headlines.return_value,
        )

    @mock.patch(f"{MODULE_PATH}.create_records")
    @mock.patch.object(ConsumerV2, "build_core_time_series")
    def test_create_core_time_series_delegates_calls_successfully(
        self,
        spy_build_core_time_series: mock.MagicMock,
        spy_create_records: mock.MagicMock,
    ):
        """
        Given an instance of the `Consumer`
        When `create_core_time_series()` is called from the object
        Then the `create_records()` function is called
            with the correct args

        Patches:
            `spy_build_core_time_series`: To check the
                `CoreTimeSeries` model instances are built
                and passed to `create_records()`
            `spy_create_records`: For the main assertion
        """
        # Given
        consumer = ConsumerV2(data=mock.Mock())

        # When
        consumer.create_core_time_series()

        # Then
        spy_build_core_time_series.assert_called_once()
        spy_create_records.assert_called_once_with(
            model_manager=consumer.core_timeseries_manager,
            model_instances=spy_build_core_time_series.return_value,
        )

    @mock.patch(f"{MODULE_PATH}.create_records")
    @mock.patch.object(ConsumerV2, "build_api_time_series")
    def test_create_api_time_series_delegates_calls_successfully(
        self,
        spy_build_api_time_series: mock.MagicMock,
        spy_create_records: mock.MagicMock,
    ):
        """
        Given an instance of the `Consumer`
        When `create_api_time_series()` is called from the object
        Then the `create_records()` function is called
            with the correct args

        Patches:
            `spy_build_api_time_series`: To check the
                `APITimeSeries` model instances are built
                and passed to `create_records()`
            `spy_create_records`: For the main assertion
        """
        # Given
        consumer = ConsumerV2(data=mock.Mock())

        # When
        consumer.create_api_time_series()

        # Then
        spy_build_api_time_series.assert_called_once()
        spy_create_records.assert_called_once_with(
            model_manager=consumer.api_timeseries_manager,
            model_instances=spy_build_api_time_series.return_value,
        )

    @mock.patch.object(ConsumerV2, "create_api_time_series")
    @mock.patch.object(ConsumerV2, "create_core_time_series")
    def test_create_core_and_api_timeseries_delegates_calls_successfully(
        self,
        spy_create_core_time_series: mock.MagicMock,
        spy_create_api_time_series: mock.MagicMock,
    ):
        """
        Given an instance of the `Consumer`
        When `create_core_and_api_timeseries()` is called from the object
        Then call is delegated for the core and api timeseries

        Patches:
            `spy_create_core_time_series`: For the main assertion
            `spy_create_api_time_series`: For the main assertion
        """
        # Given
        consumer = ConsumerV2(data=mock.Mock())

        # When
        consumer.create_core_and_api_timeseries()

        # Then
        spy_create_core_time_series.assert_called_once()
        spy_create_api_time_series.assert_called_once()
