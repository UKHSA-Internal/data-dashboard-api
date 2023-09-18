from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.crawler import Crawler
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
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

    @mock.patch.object(Crawler, "process_list_pages_for_headless_cms_api")
    def test_delegates_call_for_headless_cms_api_list_pages(
        self,
        spy_process_list_pages_for_headless_cms_api: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a list of pages
        When `process_pages()` is called from an instance of `Crawler`
        Then the `process_list_pages_for_headless_cms_api()` method is called

        Patches:
            `spy_process_list_pages_for_headless_cms_api`: For the main assertion
        """
        # Given
        fake_pages = [
            FakeTopicPageFactory._build_page(page_name="covid_19"),
            FakeTopicPageFactory._build_page(page_name="influenza"),
        ]

        # When
        crawler_with_mocked_internal_api_client.process_pages(pages=fake_pages)

        # Then
        spy_process_list_pages_for_headless_cms_api.assert_called_once()

    @mock.patch.object(Crawler, "process_detail_pages_for_headless_cms_api")
    def test_delegates_call_for_processing_each_page_headless_cms_api_detail(
        self,
        spy_process_detail_pages_for_headless_cms_api: mock.MagicMock,
        crawler_with_mocked_internal_api_client: Crawler,
    ):
        """
        Given a list of pages
        When `process_pages()` is called from an instance of `Crawler`
        Then the `process_pages_for_headless_cms_api()` method is called

        Patches:
            `spy_process_pages_for_headless_cms_api`: For the main assertion
        """
        # Given
        fake_pages = [
            FakeTopicPageFactory._build_page(page_name="covid_19"),
            FakeTopicPageFactory._build_page(page_name="influenza"),
        ]

        # When
        crawler_with_mocked_internal_api_client.process_pages(pages=fake_pages)

        # Then
        spy_process_detail_pages_for_headless_cms_api.assert_called_once_with(
            pages=fake_pages
        )

    def test_logs_when_page_sections_cannot_be_processed_eg_common_pages(
        self,
        crawler_with_mocked_internal_api_client: Crawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of `CommonPage`
        When `process_pages()` is called from an instance of `Crawler`
        Then the correct log statements are recorded
        """
        # Given
        fake_common_pages = [
            FakeCommonPageFactory.build_blank_page(title="About"),
            FakeCommonPageFactory.build_blank_page(title="Compliance"),
        ]

        # When
        crawler_with_mocked_internal_api_client.process_pages(pages=fake_common_pages)

        # Then
        for common_page in fake_common_pages:
            expected_log = f"{common_page.title} page has no dynamic content blocks. So only the headless CMS API detail has been processed"
            assert expected_log in caplog.text
