from caching.private_api.crawler.cms_blocks import CMSBlockParser

EXAMPLE_HEADLINE_NUMBERS_ROW_CARDS = [
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
    }
]


class TestGetHeadlineBlocksFromHeadlineNumberRowCards:
    def test_returns_correct_headline_number_blocks(self):
        """
        Given a list of example headline number row cards
        When `get_headline_blocks_from_headline_number_row_cards()` is called
            from the `CMSBlockParser` class
        Then the correct headline number blocks are extracted and returned
        """
        # Given
        headline_number_row_cards = EXAMPLE_HEADLINE_NUMBERS_ROW_CARDS

        # When
        headline_number_blocks = (
            CMSBlockParser.get_headline_blocks_from_headline_number_row_cards(
                headline_numbers_row_cards=headline_number_row_cards
            )
        )

        # Then
        expected_headline_number_blocks = [
            headline_number_row_cards[0]["value"]["columns"][0]["value"]["rows"][0],
            headline_number_row_cards[0]["value"]["columns"][0]["value"]["rows"][1],
            headline_number_row_cards[0]["value"]["columns"][1]["value"]["rows"][0],
        ]
        assert headline_number_blocks == expected_headline_number_blocks

    def test_returns_empty_list_for_no_headline_number_row_cards(self):
        """
        Given an empty list of headline number row cards
        When `get_headline_blocks_from_headline_number_row_cards()` is called
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        no_headline_number_row_cards = []

        # When
        headline_number_blocks = (
            CMSBlockParser.get_headline_blocks_from_headline_number_row_cards(
                headline_numbers_row_cards=no_headline_number_row_cards
            )
        )

        # Then
        assert headline_number_blocks == []
