from unittest import mock

from cms.dynamic_content.blocks_deconstruction import CMSBlockParser


class TestCMSBlockParser:
    def test_get_content_cards_from_section(self):
        """
        Given a mocked section which contains a list of content cards
        When `get_content_cards_from_section()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct content cards are returned
        """
        # Given
        mocked_content_cards = [mock.Mock()] * 3
        mocked_section = {"value": {"content": mocked_content_cards}}
        cms_block_parser = CMSBlockParser()

        # When
        retrieved_content_cards = cms_block_parser.get_content_cards_from_section(
            section=mocked_section
        )

        # Then
        assert retrieved_content_cards == mocked_content_cards

    def test_get_chart_row_cards_from_content_cards(self):
        """
        Given mocked content cards which contains a list of chart row cards
        When `get_chart_row_cards_from_content_cards()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct chart row cards are returned
        """
        # Given
        mocked_chart_cards = [{"type": "chart_row_card"}] * 3
        mocked_content_cards = [{"type": "headline_numbers_row_card"}] * 2
        mocked_content_cards += mocked_chart_cards
        cms_block_parser = CMSBlockParser()

        # When
        retrieved_chart_row_cards = (
            cms_block_parser.get_chart_row_cards_from_content_cards(
                content_cards=mocked_content_cards
            )
        )

        # Then
        # We only expect to be returned with the chart row cards
        # Therefore filtering out the headline numbers row cards
        assert retrieved_chart_row_cards == mocked_chart_cards

    def test_get_headline_numbers_row_cards_from_content_cards(self):
        """
        Given mocked content cards which contains a list of headline number row cards
        When `get_headline_numbers_row_cards_from_content_cards()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct headline numbers row cards  are returned
        """
        # Given
        mocked_headline_numbers_row_cards = [{"type": "headline_numbers_row_card"}] * 3
        mocked_content_cards = [{"type": "chart_row_card"}] * 2
        mocked_content_cards += mocked_headline_numbers_row_cards
        cms_block_parser = CMSBlockParser()

        # When
        retrieved_headline_numbers_row_cards = (
            cms_block_parser.get_headline_numbers_row_cards_from_content_cards(
                content_cards=mocked_content_cards
            )
        )

        # Then
        # We only expect to be returned with the headline numbers row cards
        # Therefore filtering out the chart row cards
        assert retrieved_headline_numbers_row_cards == mocked_headline_numbers_row_cards

    @mock.patch.object(CMSBlockParser, "get_content_cards_from_section")
    @mock.patch.object(CMSBlockParser, "get_chart_row_cards_from_content_cards")
    def test_get_chart_row_cards_from_page_section(
        self,
        spy_get_chart_row_cards_from_content_cards: mock.MagicMock,
        spy_get_content_cards_from_section: mock.MagicMock,
    ):
        """
        Given I have a page section
        When the get_chart_row_cards_from_page_section() is called
        Then the correct calls are delegated.
        """
        # Given
        mock_section = mock.Mock()
        cms_block_parser = CMSBlockParser()

        # When
        cms_block_parser.get_chart_row_cards_from_page_section(section=mock_section)

        # Then
        spy_get_content_cards_from_section.assert_called_once_with(section=mock_section)
        expected_content_cards = spy_get_content_cards_from_section.return_value
        spy_get_chart_row_cards_from_content_cards.assert_called_once_with(
            content_cards=expected_content_cards
        )
