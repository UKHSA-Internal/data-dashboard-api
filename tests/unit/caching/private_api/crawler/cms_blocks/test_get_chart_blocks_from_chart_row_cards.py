from caching.private_api.crawler.cms_blocks import CMSBlockParser

EXAMPLE_CHART_ROW_CARDS = [
    {
        "type": "chart_row_card",
        "value": {
            "columns": [
                {
                    "type": "chart_with_headline_and_trend_card",
                    "value": {
                        "title": "Cases",
                        "body": "Positive COVID-19 cases reported in England (7-day rolling average)",
                        "x_axis": "",
                        "y_axis": "",
                        "chart": [
                            {
                                "type": "plot",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_cases_countRollingMean",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "chart_type": "line_with_shaded_section",
                                    "date_from": None,
                                    "date_to": None,
                                    "label": "",
                                    "line_colour": "",
                                    "line_type": "",
                                },
                                "id": "b0ead98b-4102-48f6-b94e-ff7bcffe1dc4",
                            }
                        ],
                        "headline_number_columns": [
                            {
                                "type": "headline_number",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_headline_cases_7DayTotals",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "body": "7 days",
                                },
                                "id": "95b24a05-a015-42ed-b258-51c7ccaedbcd",
                            },
                            {
                                "type": "trend_number",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_headline_cases_7DayChange",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "body": "",
                                    "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                },
                                "id": "8c42a86e-f675-41d0-a65a-633c20ac98e3",
                            },
                        ],
                    },
                    "id": "d9b86415-9734-46be-952a-56182f0c40be",
                },
                {
                    "type": "chart_with_headline_and_trend_card",
                    "value": {
                        "title": "Deaths",
                        "body": "Deaths with COVID-19 on the death certificate in England (7-day rolling average)",
                        "x_axis": "",
                        "y_axis": "",
                        "chart": [
                            {
                                "type": "plot",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_deaths_ONSRollingMean",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "chart_type": "line_with_shaded_section",
                                    "date_from": None,
                                    "date_to": None,
                                    "label": "",
                                    "line_colour": "",
                                    "line_type": "",
                                },
                                "id": "d3b521d8-a6bb-4960-9db9-864c3d362976",
                            }
                        ],
                        "headline_number_columns": [
                            {
                                "type": "headline_number",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "body": "7 days",
                                },
                                "id": "10c92d4c-bdb1-4bcc-a8a5-d0063dcee095",
                            },
                            {
                                "type": "trend_number",
                                "value": {
                                    "topic": "COVID-19",
                                    "metric": "COVID-19_headline_ONSdeaths_7DayChange",
                                    "geography": "England",
                                    "geography_type": "Nation",
                                    "sex": "all",
                                    "age": "all",
                                    "stratum": "default",
                                    "body": "",
                                    "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
                                },
                                "id": "41ce6c59-99fe-486a-8225-341a306cc395",
                            },
                        ],
                    },
                    "id": "c18703a1-9b01-417f-8fd8-3e4db35865e5",
                },
            ]
        },
        "id": "a5acbd6c-f9b7-4d36-86f4-005c2d46debc",
    }
]


class TestGetChartBlocksFromChartRowCards:
    def test_returns_correct_chart_cards(self):
        """
        Given a list of example chart row cards
        When `get_chart_blocks_from_chart_row_cards()` is called
            from the `CMSBlockParser` class
        Then the correct chart blocks are extracted and returned
        """
        # Given
        chart_row_cards = EXAMPLE_CHART_ROW_CARDS

        # When
        chart_blocks = CMSBlockParser.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=chart_row_cards
        )

        # Then
        expected_chart_blocks = [
            chart_row_cards[0]["value"]["columns"][0]["value"],
            chart_row_cards[0]["value"]["columns"][1]["value"],
        ]
        assert chart_blocks == expected_chart_blocks

    def test_returns_empty_list_for_no_chart_row_cards(self):
        """
        Given an empty list of chart row cards
        When `get_chart_cards_from_chart_row_cards()`
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        no_chart_row_cards = []

        # When
        chart_cards = CMSBlockParser.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=no_chart_row_cards
        )

        # Then
        assert chart_cards == []
