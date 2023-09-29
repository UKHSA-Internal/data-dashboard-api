from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler import PrivateAPICrawler
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestPrivateAPICrawlerProcessPages:
    @mock.patch.object(PrivateAPICrawler, "process_all_sections_in_page")
    def test_delegates_call_for_each_page(
        self,
        spy_process_all_sections_in_page: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a list of `TopicPages`
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_pages(
            pages=fake_pages
        )

        # Then
        expected_calls = [mock.call(page=page) for page in fake_pages]
        spy_process_all_sections_in_page.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(PrivateAPICrawler, "process_list_pages_for_headless_cms_api")
    def test_delegates_call_for_headless_cms_api_list_pages(
        self,
        spy_process_list_pages_for_headless_cms_api: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a list of pages
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_pages(
            pages=fake_pages
        )

        # Then
        spy_process_list_pages_for_headless_cms_api.assert_called_once()

    @mock.patch.object(PrivateAPICrawler, "process_detail_pages_for_headless_cms_api")
    def test_delegates_call_for_processing_each_page_headless_cms_api_detail(
        self,
        spy_process_detail_pages_for_headless_cms_api: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a list of pages
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
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
        private_api_crawler_with_mocked_internal_api_client.process_pages(
            pages=fake_pages
        )

        # Then
        spy_process_detail_pages_for_headless_cms_api.assert_called_once_with(
            pages=fake_pages
        )

    def test_logs_when_page_sections_cannot_be_processed_eg_common_pages(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of `CommonPage`
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct log statements are recorded
        """
        # Given
        fake_common_pages = [
            FakeCommonPageFactory.build_blank_page(title="About"),
            FakeCommonPageFactory.build_blank_page(title="Compliance"),
        ]

        # When
        private_api_crawler_with_mocked_internal_api_client.process_pages(
            pages=fake_common_pages
        )

        # Then
        for common_page in fake_common_pages:
            expected_log = f"`{common_page.title}` page has no dynamic content blocks. So only the headless CMS API detail has been processed"
            assert expected_log in caplog.text

    def test_logs_are_recorded_for_completion_of_headless_cms_api(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of mocked `Page` objects
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct logs are made for the processing of the headless CMS API
        """
        # Given
        mocked_pages = [mock.MagicMock()] * 2
        crawler = private_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_pages(pages=mocked_pages)

        # Then
        assert (
            "Completed processing of headless CMS API, now handling content blocks"
            in caplog.text
        )

    def test_logs_are_recorded_for_processing_of_private_api_content_blocks(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of mocked `Page` objects
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct logs are made for the processing of content blocks
        """
        # Given
        mocked_pages = [mock.MagicMock()] * 2
        crawler = private_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_pages(pages=mocked_pages)

        # Then
        for mocked_page in mocked_pages:
            assert (
                f"Processing content blocks within `{mocked_page.title}` page"
                in caplog.text
            )

    def test_logs_are_recorded_with_counter_of_number_of_pages_completed(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of mocked `Page` objects
        When `process_pages()` is called
            from an instance of `PrivateAPICrawler`
        Then the correct logs are made with a counter of completed of pages
        """
        # Given
        pages_count = 10
        mocked_pages = [mock.MagicMock()] * pages_count
        crawler = private_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_pages(pages=mocked_pages)

        # Then
        for i in range(pages_count):
            index = i + 1
            assert f"Completed {index} / {pages_count} pages" in caplog.text
