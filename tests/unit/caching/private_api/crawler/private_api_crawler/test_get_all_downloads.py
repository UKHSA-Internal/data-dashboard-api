import logging
from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.cms_blocks import CMSBlockParser
from caching.private_api.crawler.dynamic_block_crawler import DynamicContentBlockCrawler
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory

logger = logging.getLogger(__name__)


class TestPrivateAPICrawlerGetAllDownloads:
    def test_create_file_name_for_chart_card_formats_correctly(
        self, private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler
    ):
        """
        Given a fake file_name
        When create_file_name_for_chart_card() is called
        Then a formatted version of the string will be returned with a file
            extension that matches the file_format provided.
        """
        # Given
        fake_file_name = "chart title name"
        fake_file_format = "csv"

        # When
        file_name = private_api_crawler_with_mocked_internal_api_client.create_filename_for_chart_card(
            file_name=fake_file_name,
            file_format=fake_file_format,
        )

        # Then
        expected_file_name = "chart_title_name.csv"
        assert expected_file_name == file_name

    @mock.patch.object(PrivateAPICrawler, "create_filename_for_chart_card")
    @mock.patch.object(DynamicContentBlockCrawler, "process_download_for_chart_block")
    def test_get_downloads_from_chart_row_columns_delegates_calls_correctly(
        self,
        spy_process_download_for_chart_block: mock.MagicMock,
        spy_create_filename_for_chart_card: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        example_chart_row_column: dict[str, str | list[dict]],
    ):
        """
        Given two faked chart_row_columns
        When the get_downloads_from_chart_row_columns() method is called
        Then process_download_for_cart_block is called twice
            and two downloads are returned.
        """
        # Given
        faked_two_row_columns = example_chart_row_column

        # When
        downloads = private_api_crawler_with_mocked_internal_api_client.get_downloads_from_chart_row_columns(
            chart_row_columns=faked_two_row_columns, file_format="csv"
        )

        # Then
        spy_create_filename_for_chart_card.assert_called()
        expected_calls = [
            mock.call(chart_block=chart_card["value"], file_format="csv")
            for chart_card in faked_two_row_columns
        ]
        spy_process_download_for_chart_block.assert_has_calls(expected_calls)
        assert len(downloads) == len(faked_two_row_columns)

    @mock.patch.object(PrivateAPICrawler, "get_downloads_from_chart_row_columns")
    def test_get_downloads_from_chart_cards_delegates_calls_correctly(
        self,
        spy_get_downloads_from_chart_row_columns: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        example_dummy_chart_row_cards,
    ):
        """
        Given a chart_row_card containing two columns
        When get_downloads_from_chard_cards() is called
        Then a single call to get_downloads_from_chart_row_columns() is made
        """
        # Given
        mocked_row_cards = example_dummy_chart_row_cards

        # When
        private_api_crawler_with_mocked_internal_api_client.get_downloads_from_chart_cards(
            chart_row_cards=mocked_row_cards, file_format="csv"
        )

        # Then
        spy_get_downloads_from_chart_row_columns.assert_called_once()

    @mock.patch.object(CMSBlockParser, "get_chart_row_cards_from_page_section")
    @mock.patch.object(PrivateAPICrawler, "get_downloads_from_chart_cards")
    def test_get_downloads_from_sections_delegates_calls_correctly(
        self,
        spy_get_downloads_from_chart_cards: mock.MagicMock,
        spy_get_chart_row_cards_from_page_section: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given: A list of sections
        When the get_downloads_from_page_sections() is called
        Then the process_chart_row_cards_from_page_section will
            be called for each section supplied.
        """
        # Given
        mock_sections = [mock.Mock()]

        # When
        private_api_crawler_with_mocked_internal_api_client.get_downloads_from_page_sections(
            sections=mock_sections, file_format="csv"
        )

        # Then
        mocked_calls = [mock.call(section=section) for section in mock_sections]
        spy_get_chart_row_cards_from_page_section.assert_has_calls(mocked_calls)
        chart_row_cards = spy_get_chart_row_cards_from_page_section.return_value
        spy_get_downloads_from_chart_cards.assert_called_with(
            chart_row_cards=chart_row_cards,
            file_format="csv",
        )

    @mock.patch.object(PrivateAPICrawler, "get_downloads_from_page_sections")
    def test_get_all_downloads_delegates_calls_correctly(
        self,
        spy_get_downloads_from_page_sections: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given: I have a list of pages
        When: Each page is passed to `get_downloads_from_page_sections()`
        Then: `get_downloads_from_page_sections()` should receive the correct
            number of calls
        """
        # Given
        fake_pages = [
            FakeTopicPageFactory._build_page(page_name="covid_19"),
            FakeTopicPageFactory._build_page(page_name="influenza"),
        ]

        # When
        private_api_crawler_with_mocked_internal_api_client.get_all_downloads(
            pages=fake_pages, file_format="csv"
        )

        # Then
        expected_pages = [
            mock.call(sections=page.body.raw_data, file_format="csv")
            for page in fake_pages
        ]
        spy_get_downloads_from_page_sections.assert_has_calls(
            expected_pages, any_order=True
        )

    @mock.patch.object(PrivateAPICrawler, "get_downloads_from_page_sections")
    def test_get_all_downloads_logs_unsupported_pages(
        self,
        mocked_get_downloads_from_page_sections: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given: A list of pages, not all containing chart data
        When: the `get_all_downloads()` function is called.
        Then: an attribution exception is caught and the page logged out
            before continuing to the next page.
        """
        # Given
        fake_pages = [
            FakeCommonPageFactory.build_blank_page(title="About"),
            FakeTopicPageFactory._build_page(page_name="covid_19"),
        ]

        # When
        private_api_crawler_with_mocked_internal_api_client.get_all_downloads(
            pages=fake_pages, file_format="csv"
        )

        # Then
        expected_log = f"Page {fake_pages[0]} does not contain chart data"
        assert expected_log in caplog.text
