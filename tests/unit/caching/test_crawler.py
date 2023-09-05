from unittest import mock

import pytest

from caching.crawler import Crawler
from caching.internal_api_client import InternalAPIClient
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


@pytest.fixture
def crawler_with_mocked_internal_api_client() -> Crawler:
    return Crawler(internal_api_client=mock.Mock())


@pytest.fixture
def example_headline_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7daytotals",
        "geography": "Croydon",
        "geography_type": "Upper Tier Local Authority",
        "body": "Last 7 days",
    }


@pytest.fixture
def example_trend_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7daychange",
        "body": "Last 7 days",
        "percentage_metric": "COVID-19_headline_ONSdeaths_7daypercentchange",
    }


@pytest.fixture
def example_chart_block() -> dict[str, str | list[dict]]:
    return {
        "title": "Admissions rate by age",
        "body": "Age breakdown of people admitted to hospital.",
        "x_axis": "stratum",
        "y_axis": "metric",
        "chart": [
            {
                "type": "plot",
                "value": {
                    "topic": "COVID-19",
                    "metric": "COVID-19_healthcare_AdmissionsByDay",
                    "chart_type": "bar",
                    "date_from": None,
                    "date_to": None,
                    "stratum": "",
                    "geography": "England",
                    "geography_type": "Nation",
                    "sex": "",
                    "age": "",
                    "label": "Admission rate",
                    "line_colour": "",
                    "line_type": "",
                },
                "id": "791efbf1-8880-4dfa-9f5d-526982ed1539",
            }
        ],
    }


class TestCrawlerInit:
    # Tests for the __init__
    def test_internal_api_client_can_be_provided_to_init(self):
        """
        Given a pre-existing `InternalAPIClient`
        When the `Crawler` class is initialized
        Then the `_internal_api_client` is set with the provided client
        """
        # Given
        mocked_internal_api_client = mock.Mock()

        # When
        crawler = Crawler(internal_api_client=mocked_internal_api_client)

        # Then
        assert crawler._internal_api_client == mocked_internal_api_client

    @mock.patch.object(InternalAPIClient, "create_api_client")
    def test_internal_api_client_can_be_provided_to_init_(
        self, mocked_create_api_client: mock.MagicMock
    ):
        """
        Given no provided pre-existing `InternalAPIClient`
        When the `Crawler` class is initialized
        Then the `_internal_api_client` is set with an `InternalAPIClient` instance

        Patches:
            `mocked_create_api_client`: To isolate the side effect of
                creating an API key and therefore interacting with the db

        """
        # Given / When
        crawler = Crawler()

        # Then
        assert isinstance(crawler._internal_api_client, InternalAPIClient)


class TestCrawlerBuildRequestData:
    def test_build_headlines_request_data(
        self,
        example_headline_number_block: dict[str, str],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a headline number block
        When `_build_headlines_request_data()` is called from an instance of `Crawler`
        Then the correct dict is returned
        """
        # Given
        headline_number_block = example_headline_number_block

        # When
        headline_number_data = (
            crawler_with_mocked_internal_api_client._build_headlines_request_data(
                headline_number_block=headline_number_block
            )
        )

        # Then
        expected_headline_request_data = {
            "topic": headline_number_block["topic"],
            "metric": headline_number_block["metric"],
            "geography": headline_number_block["geography"],
            "geography_type": headline_number_block["geography_type"],
        }
        assert headline_number_data == expected_headline_request_data

    def test_build_headlines_request_data_default_geography_fields(
        self, crawler_with_mocked_internal_api_client: Crawler
    ):
        """
        Given a headline number block which does not contain geography information
        When `_build_headlines_request_data()` is called from an instance of `Crawler`
        Then the correct dict is returned
        """
        # Given
        headline_number_block_with_no_geography_input = {
            "topic": "COVID-19",
            "metric": "COVID-19_headline_ONSdeaths_7daytotals",
            "body": "Last 7 days",
        }

        # When
        headline_number_data = (
            crawler_with_mocked_internal_api_client._build_headlines_request_data(
                headline_number_block=headline_number_block_with_no_geography_input
            )
        )

        # Then
        expected_headline_request_data = {
            "topic": headline_number_block_with_no_geography_input["topic"],
            "metric": headline_number_block_with_no_geography_input["metric"],
            "geography": "England",
            "geography_type": "Nation",
        }
        assert headline_number_data == expected_headline_request_data

    def test_build_trend_request_data(
        self,
        example_trend_number_block: dict[str, str],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a trend number block
        When `_build_trend_request_data()` is called from an instance of `Crawler`
        Then the correct dict is returned
        """
        # Given
        trend_number_block = example_trend_number_block

        # When
        trend_request_data = (
            crawler_with_mocked_internal_api_client._build_trend_request_data(
                trend_number_block=trend_number_block
            )
        )

        # Then
        expected_trend_request_data = {
            "topic": "COVID-19",
            "metric": "COVID-19_headline_ONSdeaths_7daychange",
            "percentage_metric": "COVID-19_headline_ONSdeaths_7daypercentchange",
        }
        assert trend_request_data == expected_trend_request_data

    @pytest.mark.parametrize(
        "chart_is_double_width, expected_chart_width", ([(True, 1100), (False, 515)])
    )
    def test_build_chart_request_data(
        self,
        chart_is_double_width: bool,
        expected_chart_width: int,
        example_chart_block: dict[str, str | list[dict]],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `_build_chart_request_data()` is called from an instance of `Crawler`
        Then the correct dict is returned
        """
        # Given
        chart_block_data = example_chart_block

        # When
        chart_request_data = (
            crawler_with_mocked_internal_api_client._build_chart_request_data(
                chart_block=chart_block_data,
                chart_is_double_width=chart_is_double_width,
            )
        )

        # Then
        plot_value = chart_block_data["chart"][0]["value"]
        expected_chart_request_data = {
            "plots": [
                {
                    "topic": plot_value["topic"],
                    "metric": plot_value["metric"],
                    "chart_type": plot_value["chart_type"],
                    "date_from": plot_value["date_from"],
                    "date_to": plot_value["date_to"],
                    "stratum": plot_value["stratum"],
                    "geography": plot_value["geography"],
                    "geography_type": plot_value["geography_type"],
                    "sex": plot_value["sex"],
                    "label": plot_value["label"],
                    "line_colour": plot_value["line_colour"],
                    "line_type": plot_value["line_type"],
                }
            ],
            "file_format": "svg",
            "chart_width": expected_chart_width,
            "chart_height": 260,
            "x_axis": chart_block_data["x_axis"],
            "y_axis": chart_block_data["y_axis"],
        }
        assert chart_request_data == expected_chart_request_data

    def test_build_tables_request_data(
        self,
        example_chart_block: dict[str, str | list[dict]],
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a chart block
        When `_build_tables_request_data()` is called from an instance of `Crawler`
        Then the correct dict is returned
        """
        # Given
        chart_block_data = example_chart_block

        # When
        tables_request_data = (
            crawler_with_mocked_internal_api_client._build_tables_request_data(
                chart_block=chart_block_data,
            )
        )

        # Then
        plot_value = chart_block_data["chart"][0]["value"]
        expected_tables_request_data = {
            "plots": [
                {
                    "topic": plot_value["topic"],
                    "metric": plot_value["metric"],
                    "chart_type": plot_value["chart_type"],
                    "date_from": plot_value["date_from"],
                    "date_to": plot_value["date_to"],
                    "stratum": plot_value["stratum"],
                    "geography": plot_value["geography"],
                    "geography_type": plot_value["geography_type"],
                    "sex": plot_value["sex"],
                    "label": plot_value["label"],
                    "line_colour": plot_value["line_colour"],
                    "line_type": plot_value["line_type"],
                }
            ],
        }
        assert tables_request_data == expected_tables_request_data

    def test_build_plot_data(self, crawler_with_mocked_internal_api_client: Crawler):
        """
        Given a plot value dict for a chart
        When `_build_plot_data()` is called from an instance of `Crawler`
        Then the correct plot data dict is returned
        """
        # Given
        plot_value = {
            "topic": "COVID-19",
            "metric": "COVID-19_cases_casesByDay",
            "chart_type": "bar",
            "date_from": "2023-01-01",
            "date_to": None,
            "stratum": "default",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "label": "",
            "line_colour": "BLUE",
            "line_type": "",
        }

        # When
        plot_data = crawler_with_mocked_internal_api_client._build_plot_data(
            plot_value=plot_value
        )

        # Then
        assert plot_data["topic"] == plot_value["topic"]
        assert plot_data["metric"] == plot_value["metric"]
        assert plot_data["chart_type"] == plot_value["chart_type"]
        assert plot_data["date_from"] == plot_value["date_from"]
        assert plot_data["date_to"] == plot_value["date_to"]
        assert plot_data["stratum"] == plot_value["stratum"]
        assert plot_data["geography"] == plot_value["geography"]
        assert plot_data["geography_type"] == plot_value["geography_type"]
        assert plot_data["sex"] == plot_value["sex"]
        assert plot_data["label"] == plot_value["label"]
        assert plot_data["line_colour"] == plot_value["line_colour"]
        assert plot_data["line_type"] == plot_value["line_type"]


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


class TestCrawlerProcessCards:
    @mock.patch.object(Crawler, "process_any_headline_number_block")
    def test_process_headline_numbers_row_card(
        self,
        spy_process_any_headline_number_block: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked a single headlines number row card with multiple columns
        When `process_headline_numbers_row_card()` is called
            from an instance of `Crawler`
        Then the call is delegated to the `process_any_headline_number_block()` method
            for each individual headlines number row block

        Patches:
            `spy_process_headline_numbers_row_card`: For the main assertion
                to check each headliner number row card is handled
        """
        # Given
        mocked_headline_number_blocks = [mock.Mock()] * 3
        headline_number_columns = [
            {"value": {"rows": [mocked_headline_number_blocks[0]]}},
            {
                "value": {
                    "rows": [
                        mocked_headline_number_blocks[1],
                        mocked_headline_number_blocks[2],
                    ]
                }
            },
        ]
        mocked_headline_numbers_row_card = {
            "value": {"columns": headline_number_columns}
        }

        # When
        crawler_with_mocked_internal_api_client.process_headline_numbers_row_card(
            headline_numbers_row_card=mocked_headline_numbers_row_card
        )

        # Then
        expected_calls = [
            mock.call(headline_number_block=mocked_headline_number_block)
            for mocked_headline_number_block in mocked_headline_number_blocks
        ]
        spy_process_any_headline_number_block.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(Crawler, "process_headline_numbers_row_card")
    def test_process_all_headline_numbers_row_cards(
        self,
        spy_process_headline_numbers_row_card: mock.Mock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked list of headlines number row cards
        When `process_all_headline_numbers_row_cards()` is called
            from an instance of `Crawler`
        Then the call is delegated to the `process_headline_numbers_row_card()` method
            for each individual headlines number row card

        Patches:
            `spy_process_headline_numbers_row_card`: For the main assertion
                to check each headliner number row card is handled
        """
        # Given
        mocked_headline_numbers_row_cards = [mock.Mock()] * 3

        # When
        crawler_with_mocked_internal_api_client.process_all_headline_numbers_row_cards(
            headline_numbers_row_cards=mocked_headline_numbers_row_cards
        )

        # Then
        expected_calls = [
            mock.call(headline_numbers_row_card=mocked_headline_numbers_row_card)
            for mocked_headline_numbers_row_card in mocked_headline_numbers_row_cards
        ]
        spy_process_headline_numbers_row_card.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(Crawler, "process_any_chart_card")
    def test_process_all_chart_cards(
        self,
        spy_process_any_chart_card: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked list of chart row cards
        When `process_all_chart_cards()` is called from an instance of `Crawler`
        Then the call is delegated to the `process_any_chart_card()` method
            for each individual chart row card

        Patches:
            `spy_process_any_chart_card`: For the main assertion
                to check each chart row card is handled
        """
        # Given
        mocked_chart_cards = [mock.Mock()] * 3

        mocked_chart_row_cards = [
            {"value": {"columns": [mocked_chart_cards[0]]}},
            {"value": {"columns": [mocked_chart_cards[1], mocked_chart_cards[2]]}},
        ]

        # When
        crawler_with_mocked_internal_api_client.process_all_chart_cards(
            chart_row_cards=mocked_chart_row_cards
        )

        # Then
        expected_calls = [
            mock.call(chart_card=mocked_chart_card)
            for mocked_chart_card in mocked_chart_cards
        ]
        spy_process_any_chart_card.assert_has_calls(
            calls=expected_calls, any_order=True
        )


class TestCrawlerDeconstructBlocks:
    def test_get_content_cards_from_section(
        self, crawler_with_mocked_internal_api_client: Crawler
    ):
        """
        Given a mocked section which contains a list of content cards
        When `get_content_cards_from_section()` is called
            from an instance of `Crawler`
        Then the correct content cards are returned
        """
        # Given
        mocked_content_cards = [mock.Mock()] * 3
        mocked_section = {"value": {"content": mocked_content_cards}}

        # When
        retrieved_content_cards = (
            crawler_with_mocked_internal_api_client.get_content_cards_from_section(
                section=mocked_section
            )
        )

        # Then
        assert retrieved_content_cards == mocked_content_cards

    def test_get_chart_row_cards_from_content_cards(
        self, crawler_with_mocked_internal_api_client: Crawler
    ):
        """
        Given mocked content cards which contains a list of chart row cards
        When `get_chart_row_cards_from_content_cards()` is called
            from an instance of `Crawler`
        Then the correct chart row cards are returned
        """
        # Given
        mocked_chart_cards = [{"type": "chart_row_card"}] * 3
        mocked_content_cards = [{"type": "headline_numbers_row_card"}] * 2
        mocked_content_cards += mocked_chart_cards

        # When
        retrieved_chart_row_cards = crawler_with_mocked_internal_api_client.get_chart_row_cards_from_content_cards(
            content_cards=mocked_content_cards
        )

        # Then
        # We only expect to be returned with the chart row cards
        # Therefore filtering out the headline numbers row cards
        assert retrieved_chart_row_cards == mocked_chart_cards

    def test_get_headline_numbers_row_cards_from_content_cards(
        self, crawler_with_mocked_internal_api_client: Crawler
    ):
        """
        Given mocked content cards which contains a list of headline number row cards
        When `get_headline_numbers_row_cards_from_content_cards()` is called
            from an instance of `Crawler`
        Then the correct headline numbers row cards  are returned
        """
        # Given
        mocked_headline_numbers_row_cards = [{"type": "headline_numbers_row_card"}] * 3
        mocked_content_cards = [{"type": "chart_row_card"}] * 2
        mocked_content_cards += mocked_headline_numbers_row_cards

        # When
        retrieved_headline_numbers_row_cards = crawler_with_mocked_internal_api_client.get_headline_numbers_row_cards_from_content_cards(
            content_cards=mocked_content_cards
        )

        # Then
        # We only expect to be returned with the headline numbers row cards
        # Therefore filtering out the chart row cards
        assert retrieved_headline_numbers_row_cards == mocked_headline_numbers_row_cards


class TestCrawlerProcessSections:
    @mock.patch.object(Crawler, "process_section")
    def test_process_all_sections_delegates_call_for_each_section(
        self,
        spy_process_section: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a `TopicPage`
        When `process_all_sections()` is called from an instance of `Crawler`
        Then the `process_section()` method is called for each section

        Patches:
            `spy_process_section`: For the main assertion
        """
        # Given
        fake_topic_page = FakeTopicPageFactory._build_page(page_name="covid_19")

        # When
        crawler_with_mocked_internal_api_client.process_all_sections(
            page=fake_topic_page
        )

        # Then
        expected_calls = [
            mock.call(section=section) for section in fake_topic_page.body.raw_data
        ]
        spy_process_section.assert_has_calls(calls=expected_calls)

    @mock.patch.object(Crawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_gathering_content_cards_for_each_section(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked page section
        When `process_section()` is called from an instance of `Crawler`
        Then the `get_content_cards_from_section()`
            method is called to gather content cards for that section

        Patches:
            `spy_get_content_cards_from_section`: For the main assertion
        """
        # Given
        mocked_section = mock.Mock()

        # When
        crawler_with_mocked_internal_api_client.process_section(section=mocked_section)

        # Then
        spy_get_content_cards_from_section.assert_called_once_with(
            section=mocked_section
        )

    @mock.patch.object(Crawler, "process_all_headline_numbers_row_cards")
    @mock.patch.object(Crawler, "get_headline_numbers_row_cards_from_content_cards")
    @mock.patch.object(Crawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_processing_headline_numbers_row_cards(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        spy_get_headline_numbers_row_cards_from_content_cards: mock.MagicMock,
        spy_process_all_headline_numbers_row_cards: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked section
        When `process_section()` is called from an instance of `Crawler`
        Then `get_headline_numbers_row_cards_from_content_cards()`
            is called to filter for headline number rows cards
        And then these are passed to the call to `process_all_headline_numbers_row_cards()`

        Patches:
            `spy_get_content_cards_from_section`: For the main assertion
            `spy_get_headline_numbers_row_cards_from_content_cards: To check
                that the headline number row cards are fetched from the main
                content cards
            `spy_process_all_headline_numbers_row_cards: To check that the
                previously fetched headline number row cards are then processed
        """
        # Given
        mocked_section = mock.Mock()

        # When
        crawler_with_mocked_internal_api_client.process_section(section=mocked_section)

        # Then
        # All the content cards are gathered for the section
        content_cards = spy_get_content_cards_from_section.return_value
        # The headline number row cards are filtered for
        spy_get_headline_numbers_row_cards_from_content_cards.assert_called_once_with(
            content_cards=content_cards
        )

        headline_numbers_row_cards = (
            spy_get_headline_numbers_row_cards_from_content_cards.return_value
        )
        # The headline number row cards are then passed to the method which handles processing
        spy_process_all_headline_numbers_row_cards.assert_called_once_with(
            headline_numbers_row_cards=headline_numbers_row_cards
        )

    @mock.patch.object(Crawler, "process_all_chart_cards")
    @mock.patch.object(Crawler, "get_chart_row_cards_from_content_cards")
    @mock.patch.object(Crawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_processing_chart_row_cards(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        spy_get_chart_row_cards_from_content_cards: mock.MagicMock,
        spy_process_all_chart_cards: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a mocked section
        When `process_section()` is called from an instance of `Crawler`
        Then `get_chart_row_cards_from_content_cards()`
            is called to filter for chart row cards
        And then these are passed to the call to `process_all_chart_cards()`

        Patches:
            `spy_get_content_cards_from_section`: For the main assertion
            `spy_get_chart_row_cards_from_content_cards: To check
                that the chart row cards are fetched from the main
                content cards
            `spy_process_all_chart_cards: To check that the
                previously fetched chart row cards are then processed
        """
        # Given
        mocked_section = mock.Mock()

        # When
        crawler_with_mocked_internal_api_client.process_section(section=mocked_section)

        # Then
        # All the content cards are gathered for the section
        content_cards = spy_get_content_cards_from_section.return_value
        # The chart row cards are filtered for
        spy_get_chart_row_cards_from_content_cards.assert_called_once_with(
            content_cards=content_cards
        )

        chart_row_cards = spy_get_chart_row_cards_from_content_cards.return_value
        # The chart row cards are then passed to the method which handles processing
        spy_process_all_chart_cards.assert_called_once_with(
            chart_row_cards=chart_row_cards
        )
