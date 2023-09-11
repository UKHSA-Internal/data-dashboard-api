from unittest import mock

from caching.crawler import Crawler
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestCrawlerProcessPages:
    @mock.patch.object(Crawler, "process_all_sections_in_page")
    def test_delegates_call_for_each_page(
        self,
        spy_process_all_sections_in_page: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a list of `TopicPages`
        When `process_pages()` is called from an instance of `Crawler`
        Then the `process_all_sections_in_page()` method
            is called for each page

        Patches:
            `spy_process_all_sections_in_page`: For the main assertion
        """
        # Given
        fake_pages = [
            FakeTopicPageFactory._build_page(page_name="covid_19"),
            FakeTopicPageFactory._build_page(page_name="influenza"),
        ]

        # When
        crawler_with_mocked_internal_api_client.process_pages(pages=fake_pages)

        # Then
        expected_calls = [mock.call(page=page) for page in fake_pages]
        spy_process_all_sections_in_page.assert_has_calls(
            calls=expected_calls, any_order=True
        )
