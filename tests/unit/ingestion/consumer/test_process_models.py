from unittest import mock

from ingestion.consumer import Consumer


class TestConsumerProcessModels:
    @mock.patch.object(Consumer, "create_core_headlines")
    @mock.patch.object(Consumer, "clear_stale_headlines")
    def test_process_core_headlines(
        self,
        spy_clear_stale_headlines: mock.MagicMock,
        spy_create_core_headlines: mock.MagicMock,
        example_headline_data,
    ):
        """
        Given incoming headline data
        When `process_core_headlines()` is called
            from an instance of the `Consumer`
        Then the `clear_stale_headlines()` method is called first
        And then the `create_core_headlines()` method is called after
        """
        # Given
        spy_manager = mock.Mock()
        spy_manager.attach_mock(spy_clear_stale_headlines, "spy_clear_stale_headlines")
        spy_manager.attach_mock(spy_create_core_headlines, "spy_create_core_headlines")
        consumer = Consumer(source_data=example_headline_data)

        # When
        consumer.process_core_headlines()

        # Then
        expected_calls = [
            mock.call.spy_clear_stale_headlines,
            mock.call.spy_create_core_headlines,
        ]
        spy_manager.assert_has_calls(calls=expected_calls, any_order=False)

    @mock.patch.object(Consumer, "create_core_and_api_timeseries")
    @mock.patch.object(Consumer, "clear_stale_timeseries")
    def test_process_timeseries(
        self,
        spy_clear_stale_timeseries: mock.MagicMock,
        spy_create_core_and_api_timeseries: mock.MagicMock,
        example_headline_data,
    ):
        """
        Given incoming timeseries data
        When `process_core_and_api_timeseries()` is called
            from an instance of the `Consumer`
        Then the `clear_stale_timeseries()` method is called first
        And then the `create_core_and_api_timeseries()` method is called after
        """
        # Given
        spy_manager = mock.Mock()
        spy_manager.attach_mock(
            spy_clear_stale_timeseries, "spy_clear_stale_timeseries"
        )
        spy_manager.attach_mock(
            spy_create_core_and_api_timeseries, "spy_create_core_and_api_timeseries"
        )
        consumer = Consumer(source_data=example_headline_data)

        # When
        consumer.process_core_and_api_timeseries()

        # Then
        expected_calls = [
            mock.call.spy_clear_stale_timeseries,
            mock.call.spy_create_core_and_api_timeseries,
        ]
        spy_manager.assert_has_calls(calls=expected_calls, any_order=False)
