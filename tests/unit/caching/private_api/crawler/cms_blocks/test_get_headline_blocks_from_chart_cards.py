from caching.private_api.crawler.cms_blocks import CMSBlockParser

EXAMPLE_CHART_CARDS = [
    {
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
    {
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
]


class TestGetHeadlineBlocksFromChartCards:
    def test_returns_correct_headline_blocks(self):
        """
        Given a list of example chart blocks
        When `get_headline_blocks_from_chart_blocks()` is called
            from the `CMSBlockParser` class
        Then the correct headline number blocks are extracted and returned
        """
        # Given
        chart_blocks = EXAMPLE_CHART_CARDS

        # When
        headline_blocks = CMSBlockParser.get_headline_blocks_from_chart_blocks(
            chart_blocks=chart_blocks
        )

        # Then
        expected_headline_blocks = [
            chart_blocks[0]["headline_number_columns"][0],
            chart_blocks[0]["headline_number_columns"][1],
            chart_blocks[1]["headline_number_columns"][0],
            chart_blocks[1]["headline_number_columns"][1],
        ]
        assert headline_blocks == expected_headline_blocks

    def test_returns_empty_list_for_no_chart_blocks(self):
        """
        Given an empty list of chart blocks
        When `get_headline_blocks_from_chart_blocks()` is called
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        no_chart_blocks = []

        # When
        headline_number_blocks = CMSBlockParser.get_headline_blocks_from_chart_blocks(
            chart_blocks=no_chart_blocks
        )

        # Then
        assert headline_number_blocks == []
