from unittest import mock

import pytest

from caching.crawler import Crawler


class TestCrawlerProcessBlocks:
    @mock.patch.object(Crawler, "process_any_headline_number_block")
    @mock.patch.object(Crawler, "process_chart_block")
    def test_process_chart_with_headline_and_trend_card(
        self,
        spy_process_chart_block: mock.MagicMock,
        spy_process_any_headline_number_block: mock.MagicMock,
        example_chart_block: dict[str, str | list[dict]],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `process_chart_with_headline_and_trend_card()` is called
            from an instance of `Crawler`
        Then the call is delegated
            to the `process_chart_block()` & `_process_any_headline_number_block()`
            methods accordingly

        Patches:
            `spy_process_chart_block`: To check the call is made
                to handle the chart itself
            `spy_process_any_headline_number_block`: To check the
                call is made to handle each headline number block
        """
        # Given
        mocked_headline_number_columns = [mock.Mock(), mock.Mock()]
        example_chart_block["headline_number_columns"] = mocked_headline_number_columns
        chart_block = {"value": example_chart_block}

        # When
        crawler_with_mocked_internal_api_client.process_chart_with_headline_and_trend_card(
            chart_with_headline_and_trend_card=chart_block,
        )

        # Then
        # Check the `process_chart_block()` method is delegated
        # to in order to handle the chart block itself
        spy_process_chart_block.assert_called_once_with(chart_block=chart_block)

        # Check the `process_any_headline_number_block()` method is delegated
        # to in order to handle any of the headline numbers which accompany the chart
        expected_calls = [
            mock.call(headline_number_block=mocked_headline_number_column)
            for mocked_headline_number_column in mocked_headline_number_columns
        ]
        spy_process_any_headline_number_block.assert_has_calls(calls=expected_calls)

    @mock.patch.object(Crawler, "process_chart_with_headline_and_trend_card")
    @mock.patch.object(Crawler, "process_chart_block")
    def test_process_any_chart_card_for_chart_cards(
        self,
        spy_process_chart_block: mock.MagicMock,
        spy_process_chart_with_headline_and_trend_card: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake chart card which has "type" key of value "chart_card"
        When `process_any_chart_card()` is called from an instance of `Crawler`
        Then the call is delegated to the `process_chart_block()` method
        And the `process_chart_with_headline_and_trend_card()` is not called

        Patches:
            `spy_process_chart_block`: To check the call is made
                to handle the chart itself
            `spy_process_any_headline_number_block`: To check this
            is not called as this is a standalone chart card
        """
        # Given
        fake_chart_card = {"type": "chart_card"}

        # When
        crawler_with_mocked_internal_api_client.process_any_chart_card(
            chart_card=fake_chart_card,
        )

        # Then
        spy_process_chart_block.assert_called_once_with(
            chart_block=fake_chart_card,
        )
        spy_process_chart_with_headline_and_trend_card.assert_not_called()

    @mock.patch.object(Crawler, "process_chart_with_headline_and_trend_card")
    @mock.patch.object(Crawler, "process_chart_block")
    def test_process_any_chart_card_for_chart_with_headline_and_trend_cards(
        self,
        spy_process_chart_block: mock.MagicMock,
        spy_process_chart_with_headline_and_trend_card: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake chart card which has "type" key of value "chart_with_headline_and_trend_card"
        When `process_any_chart_card()` is called from an instance of `Crawler`
        Then the call is delegated to the `process_chart_with_headline_and_trend_card()` method
        And the `process_chart_block()` is not called

        Patches:
            `spy_process_chart_block`: To check the call is not made
                as this is a chart with headline and trend card
            `spy_process_any_headline_number_block`: To check this
                is called correctly
        """
        # Given
        fake_chart_card = {"type": "chart_with_headline_and_trend_card"}

        # When
        crawler_with_mocked_internal_api_client.process_any_chart_card(
            chart_card=fake_chart_card,
        )

        # Then
        spy_process_chart_with_headline_and_trend_card.assert_called_once_with(
            chart_with_headline_and_trend_card=fake_chart_card,
        )
        spy_process_chart_block.assert_not_called()

    def test_process_any_chart_card_raises_error_for_invalid_input(
        self,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake chart card which has an invalid "type" key
        When `process_any_chart_card()` is called from an instance of `Crawler`
        Then a `ValueError` is raised
        """
        # Given
        fake_chart_card = {"type": "invalid_card_type"}

        # When / Then
        with pytest.raises(ValueError):
            crawler_with_mocked_internal_api_client.process_any_chart_card(
                chart_card=fake_chart_card
            )

    @mock.patch.object(Crawler, "process_trend_number_block")
    @mock.patch.object(Crawler, "process_headline_number_block")
    def test_process_any_headline_number_block_for_trend_number_block(
        self,
        spy_process_headline_number_block: mock.MagicMock,
        spy_process_trend_number_block: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake headline number block which has a "type" key of value "trend_number"
        When `process_any_headline_number_block()` is called from an instance of `Crawler`
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
        crawler_with_mocked_internal_api_client.process_any_headline_number_block(
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
    @mock.patch.object(Crawler, "process_trend_number_block")
    @mock.patch.object(Crawler, "process_headline_number_block")
    def test_process_any_headline_number_block_for_trend_number_block(
        self,
        spy_process_headline_number_block: mock.MagicMock,
        spy_process_trend_number_block: mock.MagicMock,
        headline_number_block_type: str,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake headline number block which has a "type" key of value "headline_number"
        When `process_any_headline_number_block()` is called from an instance of `Crawler`
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
        crawler_with_mocked_internal_api_client.process_any_headline_number_block(
            headline_number_block=fake_headline_number_block,
        )

        # Then
        spy_process_headline_number_block.assert_called_once_with(
            headline_number_block=fake_headline_number_block,
        )
        spy_process_trend_number_block.assert_not_called()

    def test_process_any_headline_number_block_raises_error_for_invalid_input(
        self,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a fake headline number block which has an invalid "type" key
        When `process_any_headline_number_block()` is called from an instance of `Crawler`
        Then a `ValueError` is raised
        """
        # Given
        fake_headline_number_block = {"type": "invalid_block_type"}

        # When / Then
        with pytest.raises(ValueError):
            crawler_with_mocked_internal_api_client.process_any_headline_number_block(
                headline_number_block=fake_headline_number_block
            )


class TestCrawlerProcessIndividualBlocks:
    def test_process_trend_number_block(
        self,
        example_trend_number_block: dict[str, str],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a trend number block
        When `process_trend_number_block()` is called from an instance of `Crawler`
        Then the call is delegated
            to the `hit_trends_endpoint()` on the `InternalAPIClient`
        """
        # Given
        trend_number_block = {"value": example_trend_number_block}
        spy_internal_api_client: mock.Mock = (
            crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        crawler_with_mocked_internal_api_client.process_trend_number_block(
            trend_number_block=trend_number_block
        )

        # Then
        expected_data = {
            "topic": example_trend_number_block["topic"],
            "metric": example_trend_number_block["metric"],
            "percentage_metric": example_trend_number_block["percentage_metric"],
        }
        spy_internal_api_client.hit_trends_endpoint.assert_called_once_with(
            data=expected_data
        )

    def test_process_headline_number_block(
        self,
        example_headline_number_block: dict[str, str],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a headline number block
        When `process_headline_number_block()` is called from an instance of `Crawler`
        Then the call is delegated
            to the `hit_headlines_endpoint()` on the `InternalAPIClient`
        """
        # Given
        headline_number_block = {"value": example_headline_number_block}
        spy_internal_api_client: mock.Mock = (
            crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        crawler_with_mocked_internal_api_client.process_headline_number_block(
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
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called from an instance of `Crawler`
        Then the call is delegated to the `hit_tables_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        chart_block = {"value": example_chart_block}
        spy_internal_api_client: mock.Mock = (
            crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=chart_block,
        )

        # Then
        expected_tables_request_data = (
            crawler_with_mocked_internal_api_client._build_tables_request_data(
                chart_block=example_chart_block
            )
        )
        spy_internal_api_client.hit_tables_endpoint.assert_called_once_with(
            data=expected_tables_request_data
        )

    def test_process_chart_block_hits_downloads_endpoint(
        self,
        example_chart_block: dict[str, str | list[dict]],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called from an instance of `Crawler`
        Then the call is delegated to the `hit_downloads_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        chart_block = {"value": example_chart_block}
        spy_internal_api_client: mock.Mock = (
            crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=chart_block,
        )

        # Then
        expected_downloads_request_data = (
            crawler_with_mocked_internal_api_client._build_downloads_request_data(
                chart_block=example_chart_block
            )
        )
        spy_internal_api_client.hit_downloads_endpoint.assert_called_once_with(
            data=expected_downloads_request_data
        )

    def test_process_chart_block_hits_charts_endpoint(
        self,
        example_chart_block: dict[str, str | list[dict]],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `process_chart_block()` is called from an instance of `Crawler`
        Then the call is delegated to the `hit_charts_endpoint()`
            on the `InternalAPIClient`
        """
        # Given
        chart_block = {"value": example_chart_block}
        spy_internal_api_client: mock.Mock = (
            crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        crawler_with_mocked_internal_api_client.process_chart_block(
            chart_block=chart_block,
        )

        # Then
        # We expect the chart request to be hit twice
        # For the double and single width charts
        expected_charts_request_data_for_double_width_chart = (
            crawler_with_mocked_internal_api_client._build_chart_request_data(
                chart_block=example_chart_block,
                chart_is_double_width=True,
            )
        )
        expected_charts_request_data_for_single_width_chart = (
            crawler_with_mocked_internal_api_client._build_chart_request_data(
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
