import pytest

from caching.crawler import Crawler


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
                    "age": plot_value["age"],
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
                    "age": plot_value["age"],
                    "label": plot_value["label"],
                    "line_colour": plot_value["line_colour"],
                    "line_type": plot_value["line_type"],
                }
            ],
            "x_axis": chart_block_data["x_axis"],
            "y_axis": chart_block_data["y_axis"],
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
            "age": "all",
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
        assert plot_data["age"] == plot_value["age"]
        assert plot_data["label"] == plot_value["label"]
        assert plot_data["line_colour"] == plot_value["line_colour"]
        assert plot_data["line_type"] == plot_value["line_type"]
