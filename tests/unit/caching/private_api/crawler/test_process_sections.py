from unittest import mock

from caching.private_api.crawler import PrivateAPICrawler
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestPrivateAPICrawlerProcessSections:
    @mock.patch.object(PrivateAPICrawler, "process_section")
    def test_process_all_sections_in_page_delegates_call_for_each_section(
        self,
        spy_process_section: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a `TopicPage`
        When `process_all_sections_in_page()` is called
            from an instance of `PrivateAPICrawler`
        Then the `process_section()` method is called for each section

        Patches:
            `spy_process_section`: For the main assertion
        """
        # Given
        fake_topic_page = FakeTopicPageFactory._build_page(page_name="covid_19")

        # When
        private_api_crawler_with_mocked_internal_api_client.process_all_sections_in_page(
            page=fake_topic_page
        )

        # Then
        expected_calls = [
            mock.call(section=section) for section in fake_topic_page.body.raw_data
        ]
        spy_process_section.assert_has_calls(calls=expected_calls)

    @mock.patch.object(PrivateAPICrawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_gathering_content_cards_for_each_section(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked page section
        When `process_section()` is called
            from an instance of `PrivateAPICrawler`
        Then the `get_content_cards_from_section()`
            method is called to gather content cards for that section

        Patches:
            `spy_get_content_cards_from_section`: For the main assertion
        """
        # Given
        mocked_section = mock.Mock()

        # When
        private_api_crawler_with_mocked_internal_api_client.process_section(
            section=mocked_section
        )

        # Then
        spy_get_content_cards_from_section.assert_called_once_with(
            section=mocked_section
        )

    @mock.patch.object(PrivateAPICrawler, "process_all_headline_numbers_row_cards")
    @mock.patch.object(
        PrivateAPICrawler, "get_headline_numbers_row_cards_from_content_cards"
    )
    @mock.patch.object(PrivateAPICrawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_processing_headline_numbers_row_cards(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        spy_get_headline_numbers_row_cards_from_content_cards: mock.MagicMock,
        spy_process_all_headline_numbers_row_cards: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked section
        When `process_section()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_section(
            section=mocked_section
        )

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

    @mock.patch.object(PrivateAPICrawler, "process_all_chart_cards")
    @mock.patch.object(PrivateAPICrawler, "get_chart_row_cards_from_content_cards")
    @mock.patch.object(PrivateAPICrawler, "get_content_cards_from_section")
    def test_process_section_delegates_call_for_processing_chart_row_cards(
        self,
        spy_get_content_cards_from_section: mock.MagicMock,
        spy_get_chart_row_cards_from_content_cards: mock.MagicMock,
        spy_process_all_chart_cards: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked section
        When `process_section()` is called from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_section(
            section=mocked_section
        )

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
