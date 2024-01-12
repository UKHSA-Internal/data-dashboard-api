from unittest import mock

import pytest

from caching.private_api.crawler.dynamic_block_crawler import DynamicContentBlockCrawler


class TestDynamicContentBlockCrawlerProcessBlocks:
    @mock.patch.object(DynamicContentBlockCrawler, "process_trend_number_block")
    @mock.patch.object(DynamicContentBlockCrawler, "process_headline_number_block")
    def test_process_any_headline_number_block_for_trend_number_block(
        self,
        spy_process_headline_number_block: mock.MagicMock,
        spy_process_trend_number_block: mock.MagicMock,
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a fake headline number block which has a "type" key of value "trend_number"
        When `process_any_headline_number_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated to the `process_trend_number_block()` method
        And `process_headline_number_block()` is not called

        Patches:
            `process_headline_number_block`: To check the call is not made
                as this is a trend number block
            `process_trend_number_block`: To check this is called correctly
        """
        # Given
        fake_headline_number_block = {"type": "trend_number"}

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_any_headline_number_block(
            headline_number_block=fake_headline_number_block,
        )

        # Then
        spy_process_trend_number_block.assert_called_once_with(
            trend_number_block=fake_headline_number_block,
        )
        spy_process_headline_number_block.assert_not_called()

    @pytest.mark.parametrize(
        "headline_number_block_type", ["headline_number", "percentage_number"]
    )
    @mock.patch.object(DynamicContentBlockCrawler, "process_trend_number_block")
    @mock.patch.object(DynamicContentBlockCrawler, "process_headline_number_block")
    def test_process_any_headline_number_block_for_headline_and_percentage_number_blocks(
        self,
        spy_process_headline_number_block: mock.MagicMock,
        spy_process_trend_number_block: mock.MagicMock,
        headline_number_block_type: str,
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a fake headline number block which has a "type" key of value "headline_number"
        When `process_any_headline_number_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated to the `process_headline_number_block()` method
        And `process_trend_number_block()` is not called

        Patches:
            `process_headline_number_block`: To check the call is not made
                as this is a headline/percentage number block
            `process_trend_number_block`: To check this is called correctly
        """
        # Given
        fake_headline_number_block = {"type": headline_number_block_type}

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_any_headline_number_block(
            headline_number_block=fake_headline_number_block,
        )

        # Then
        spy_process_headline_number_block.assert_called_once_with(
            headline_number_block=fake_headline_number_block,
        )
        spy_process_trend_number_block.assert_not_called()

    def test_process_any_headline_number_block_raises_error_for_invalid_input(
        self,
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a fake headline number block which has an invalid "type" key
        When `process_any_headline_number_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then a `ValueError` is raised
        """
        # Given
        fake_headline_number_block = {"type": "invalid_block_type"}

        # When / Then
        with pytest.raises(ValueError):
            dynamic_content_block_crawler_with_mocked_internal_api_client.process_any_headline_number_block(
                headline_number_block=fake_headline_number_block
            )


class TestCrawlerProcessIndividualBlocks:
    def test_process_trend_number_block(
        self,
        example_trend_number_block: dict[str, str],
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a trend number block
        When `process_trend_number_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated
            to the `hit_trends_endpoint()` on the `InternalAPIClient`
        """
        # Given
        trend_number_block = {"value": example_trend_number_block}
        spy_internal_api_client: mock.Mock = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_trend_number_block(
            trend_number_block=trend_number_block
        )

        # Then
        expected_data = {
            "topic": example_trend_number_block["topic"],
            "metric": example_trend_number_block["metric"],
            "percentage_metric": example_trend_number_block["percentage_metric"],
            "geography": example_trend_number_block["geography"],
            "geography_type": example_trend_number_block["geography_type"],
            "sex": example_trend_number_block["sex"],
            "age": example_trend_number_block["age"],
            "stratum": example_trend_number_block["stratum"],
        }
        spy_internal_api_client.hit_trends_endpoint.assert_called_once_with(
            data=expected_data
        )

    def test_process_headline_number_block(
        self,
        example_headline_number_block: dict[str, str],
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a headline number block
        When `process_headline_number_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated
            to the `hit_headlines_endpoint()` on the `InternalAPIClient`
        """
        # Given
        headline_number_block = {"value": example_headline_number_block}
        spy_internal_api_client: mock.Mock = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_headline_number_block(
            headline_number_block=headline_number_block
        )

        # Then
        expected_data = {
            "topic": example_headline_number_block["topic"],
            "metric": example_headline_number_block["metric"],
            "geography": example_headline_number_block["geography"],
            "geography_type": example_headline_number_block["geography_type"],
            "sex": example_headline_number_block["sex"],
            "age": example_headline_number_block["age"],
            "stratum": example_headline_number_block["stratum"],
        }
        spy_internal_api_client.hit_headlines_endpoint.assert_called_once_with(
            data=expected_data
        )

    def test_process_chart_block_hits_tables_endpoint(
        self,
        example_chart_block: dict[str, str | list[dict]],
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated to the `hit_tables_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client: mock.Mock = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=example_chart_block,
        )

        # Then
        request_payload_builder = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._request_payload_builder
        )
        expected_tables_request_data = (
            request_payload_builder.build_tables_request_data(
                chart_block=example_chart_block
            )
        )
        spy_internal_api_client.hit_tables_endpoint.assert_called_once_with(
            data=expected_tables_request_data
        )

    def test_process_chart_block_hits_downloads_endpoint(
        self,
        example_chart_block: dict[str, str | list[dict]],
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated to the `hit_downloads_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        file_format = "csv"
        spy_internal_api_client: mock.Mock = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=example_chart_block,
        )

        # Then
        request_payload_builder = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._request_payload_builder
        )
        expected_downloads_request_data = (
            request_payload_builder.build_downloads_request_data(
                chart_block=example_chart_block,
                file_format=file_format,
            )
        )
        spy_internal_api_client.hit_downloads_endpoint.assert_called_once_with(
            data=expected_downloads_request_data
        )

    def test_process_chart_block_hits_charts_endpoint(
        self,
        example_chart_block: dict[str, str | list[dict]],
        dynamic_content_block_crawler_with_mocked_internal_api_client: DynamicContentBlockCrawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called
            from an instance of `DynamicContentBlockCrawler`
        Then the call is delegated to the `hit_charts_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client: mock.Mock = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        dynamic_content_block_crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=example_chart_block,
        )

        # Then
        # We expect the chart request to be hit twice
        # For the double and single width charts
        request_payload_builder = (
            dynamic_content_block_crawler_with_mocked_internal_api_client._request_payload_builder
        )
        expected_charts_request_data_for_double_width_chart = (
            request_payload_builder.build_chart_request_data(
                chart_block=example_chart_block,
                chart_is_double_width=True,
            )
        )
        expected_charts_request_data_for_single_width_chart = (
            request_payload_builder.build_chart_request_data(
                chart_block=example_chart_block,
                chart_is_double_width=False,
            )
        )
        expected_calls = [
            mock.call(data=expected_charts_request_data_for_double_width_chart),
            mock.call(data=expected_charts_request_data_for_single_width_chart),
        ]
        spy_internal_api_client.hit_charts_endpoint.assert_has_calls(
            calls=expected_calls, any_order=True
        )
