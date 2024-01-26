from caching.private_api.crawler.cms_blocks import CMSBlockParser

EXAMPLE_SECTION = {
    "type": "section",
    "value": {
        "heading": "COVID-19",
        "content": [
            {
                "type": "text_card",
                "value": {
                    "body": '<p data-block-key="6du8j">Summary of COVID-19 data. For more detailed data, go to the <a id="5" linktype="page">COVID-19 page</a>.</p>'
                },
                "id": "6a399089-6e24-4010-a484-a12745d38872",
            },
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
                                            "body": "7 days",
                                            "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                        },
                                        "id": "a57a4ad5-6b52-45a6-acfd-2fe208cb5617",
                                    },
                                ],
                            },
                            "id": "ff081d2a-e235-4bc2-9b09-220f8fe20494",
                        },
                        {
                            "type": "column",
                            "value": {
                                "title": "Testing",
                                "rows": [
                                    {
                                        "type": "percentage_number",
                                        "value": {
                                            "topic": "COVID-19",
                                            "metric": "COVID-19_headline_positivity_latest",
                                            "geography": "England",
                                            "geography_type": "Nation",
                                            "sex": "all",
                                            "age": "all",
                                            "stratum": "default",
                                            "body": "Virus tests positivity",
                                        },
                                        "id": "36746bcd-1dce-4e5e-81f8-60c8b9994540",
                                    }
                                ],
                            },
                            "id": "1e3bf214-88e4-4cf4-9b78-3ad7eabb2eaa",
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


class TestCMSBlockParserGetAllHeadlineBlocksFromSection:
    def test_returns_correct_headline_blocks(self, example_headline_number_block):
        """
        Given a section containing headline blocks
            in a mixture of headline number row cards
            as well as within chart cards
        When `get_all_headline_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then the correct headline blocks are returned
        """
        # Given
        section = EXAMPLE_SECTION

        # When
        headline_blocks = CMSBlockParser.get_all_headline_blocks_from_section(
            section=section
        )

        # Then
        expected_headline_blocks = [
            # The 1st content card is a text card, so nothing to extract there
            # The 2nd content card is headline numbers row card with 2 columns
            section["value"]["content"][1]["value"]["columns"][0]["value"]["rows"][0],
            section["value"]["content"][1]["value"]["columns"][0]["value"]["rows"][1],
            section["value"]["content"][1]["value"]["columns"][1]["value"]["rows"][0],
            # The 3rd content card is a chart row card which has 2 chart cards within it
            # The 1st chart card has multiple headline block within it
            section["value"]["content"][2]["value"]["columns"][0]["value"][
                "headline_number_columns"
            ][0],
            section["value"]["content"][2]["value"]["columns"][0]["value"][
                "headline_number_columns"
            ][1],
            # The other chart card contains no headline blocks
        ]
        assert headline_blocks == expected_headline_blocks
