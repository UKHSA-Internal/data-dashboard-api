from caching.private_api.crawler.cms_blocks import CMSBlockParser

EXAMPLE_SECTION = {
    "type": "section",
    "value": {
        "heading": "COVID-19",
        "content": [
            {
                "type": "headline_numbers_row_card",
                "value": {
                    "columns": [
                        {
                            "type": "column",
                            "value": {
                                "title": "Cases",
                                "rows": [
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
                                            "body": "Weekly",
                                        },
                                        "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
                                    }
                                ],
                            },
                            "id": "ff081d2a-e235-4bc2-9b09-220f8fe20494",
                        },
                    ]
                },
                "id": "e285caf4-ae79-4c76-bcb7-426d6e66cb8a",
            },
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
                                "headline_number_columns": [],
                            },
                            "id": "c18703a1-9b01-417f-8fd8-3e4db35865e5",
                        },
                    ]
                },
                "id": "a5acbd6c-f9b7-4d36-86f4-005c2d46debc",
            },
        ],
    },
    "id": "1f53f495-e8d1-45a3-bd34-5d27878c20fc",
}


class TestCMSBlockParserGetAllChartBlocksFromSection:
    def test_returns_correct_chart_blocks(self):
        """
        Given a section containing chart blocks within chart cards
        When `get_all_chart_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then the correct chart blocks are returned
        """
        # Given
        section = EXAMPLE_SECTION

        # When
        chart_blocks = CMSBlockParser.get_all_chart_blocks_from_section(section=section)

        # Then
        expected_chart_blocks = [
            # The 1st content card is a headline numbers row card, so nothing to extract there
            section["value"]["content"][1]["value"]["columns"][0]["value"],
            section["value"]["content"][1]["value"]["columns"][1]["value"],
            # The 2nd content card is a chart row card which contains 1 chart in each of the 2 rows.
            # So we expect to extract 2 chart blocks to be extracted
        ]
        assert chart_blocks == expected_chart_blocks
