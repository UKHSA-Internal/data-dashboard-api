from unittest import mock

from caching.crawler import Crawler


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
