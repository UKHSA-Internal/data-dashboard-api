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

    def test_process_section_delegates_calls_for_headline_number_blocks(self):
        """
        Given a mocked section
        When `process_all_sections_in_page()` is called
            from an instance of `PrivateAPICrawler`
        Then `get_all_headline_blocks_from_section()`
            is called from the `CMSBlockParser`
        And these blocks are passed to
            `process_all_headline_number_blocks()` from the
            `DynamicContentBlockCrawler`
        """
        # Given
        mocked_section = mock.Mock()
        spy_cms_block_parser = mock.Mock()
        spy_dynamic_content_block_crawler = mock.Mock()
        private_api_crawler = PrivateAPICrawler(
            internal_api_client=mock.Mock(),
            cms_block_parser=spy_cms_block_parser,
            dynamic_content_block_crawler=spy_dynamic_content_block_crawler,
        )

        # When
        private_api_crawler.process_section(section=mocked_section)

        # Then
        spy_cms_block_parser.get_all_headline_blocks_from_section.assert_called_once_with(
            section=mocked_section
        )

        expected_headline_number_blocks = (
            spy_cms_block_parser.get_all_headline_blocks_from_section.return_value
        )
        spy_dynamic_content_block_crawler.process_all_headline_number_blocks.assert_called_once_with(
            headline_number_blocks=expected_headline_number_blocks
        )

    def test_process_section_delegates_calls_for_chart_blocks(self):
        """
        Given a mocked section
        When `process_all_sections_in_page()` is called
            from an instance of `PrivateAPICrawler`
        Then `get_all_chart_blocks_from_section()`
            is called from the `CMSBlockParser`
        And these blocks are passed to
            `process_all_chart_blocks()` from the
            `DynamicContentBlockCrawler`
        """
        # Given
        mocked_section = mock.Mock()
        spy_cms_block_parser = mock.Mock()
        spy_dynamic_content_block_crawler = mock.Mock()
        private_api_crawler = PrivateAPICrawler(
            internal_api_client=mock.Mock(),
            cms_block_parser=spy_cms_block_parser,
            dynamic_content_block_crawler=spy_dynamic_content_block_crawler,
        )

        # When
        private_api_crawler.process_section(section=mocked_section)

        # Then
        spy_cms_block_parser.get_all_chart_blocks_from_section.assert_called_once_with(
            section=mocked_section
        )

        expected_chart_blocks = (
            spy_cms_block_parser.get_all_chart_blocks_from_section.return_value
        )
        spy_dynamic_content_block_crawler.process_all_chart_blocks.assert_called_once_with(
            chart_blocks=expected_chart_blocks
        )
