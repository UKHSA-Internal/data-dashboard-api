from unittest import mock

from caching.private_api.crawler import PrivateAPICrawler


class TestPrivateAPICrawlerProcessCards:
    @mock.patch.object(PrivateAPICrawler, "process_any_headline_number_block")
    def test_process_headline_numbers_row_card(
        self,
        spy_process_any_headline_number_block: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked a single headlines number row card with multiple columns
        When `process_headline_numbers_row_card()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_headline_numbers_row_card(
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

    @mock.patch.object(PrivateAPICrawler, "process_headline_numbers_row_card")
    def test_process_all_headline_numbers_row_cards(
        self,
        spy_process_headline_numbers_row_card: mock.Mock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked list of headlines number row cards
        When `process_all_headline_numbers_row_cards()` is called
            from an instance of `PrivateAPICrawler`
        Then the call is delegated to the `process_headline_numbers_row_card()` method
            for each individual headlines number row card

        Patches:
            `spy_process_headline_numbers_row_card`: For the main assertion
                to check each headliner number row card is handled
        """
        # Given
        mocked_headline_numbers_row_cards = [mock.Mock()] * 3

        # When
        private_api_crawler_with_mocked_internal_api_client.process_all_headline_numbers_row_cards(
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

    @mock.patch.object(PrivateAPICrawler, "process_any_chart_card")
    def test_process_all_chart_cards(
        self,
        spy_process_any_chart_card: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked list of chart row cards
        When `process_all_chart_cards()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_all_chart_cards(
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
