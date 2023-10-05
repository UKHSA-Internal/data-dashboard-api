from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler import PrivateAPICrawler
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestPrivateAPICrawlerProcessHeadlessCMSAPI:
    def test_process_list_pages_for_headless_cms_api_delegates_call_to_api_client(
        self, private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler
    ):
        """
        Given a mocked `InternalAPIClient`
        When `process_list_pages_for_headless_cms_api()`
            is called from an instance of `PrivateAPICrawler`
        Then the call is delegated to the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client = (
            private_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        private_api_crawler_with_mocked_internal_api_client.process_list_pages_for_headless_cms_api()

        # Then
        spy_internal_api_client.hit_pages_list_endpoint.assert_called_once()
        spy_internal_api_client.hit_pages_list_endpoint_for_all_page_types.assert_called_once()

    @mock.patch.object(
        PrivateAPICrawler, "process_individual_page_for_headless_cms_api"
    )
    def test_process_detail_pages_for_headless_cms_api_delegates_call_for_each_page(
        self,
        spy_process_individual_page_for_headless_cms_api: mock.MagicMock,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a number of pages
        When `process_detail_pages_for_headless_cms_api()`
            is called from an instance of `PrivateAPICrawler`
        Then the `process_individual_page_for_headless_cms_api()` method
            is called for each section

        Patches:
            `spy_process_individual_page_for_headless_cms_api`: For the main assertion
        """
        # Given
        fake_topic_page = FakeTopicPageFactory._build_page(page_name="covid_19")
        fake_common_page = FakeCommonPageFactory.build_blank_page(title="About")
        pages = [fake_common_page, fake_topic_page]

        # When
        private_api_crawler_with_mocked_internal_api_client.process_detail_pages_for_headless_cms_api(
            pages=pages
        )

        # Then
        expected_calls = [mock.call(page=page) for page in pages]
        spy_process_individual_page_for_headless_cms_api.assert_has_calls(
            calls=expected_calls
        )

    def test_process_individual_page_for_headless_cms_api_delegates_call_to_api_client(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
    ):
        """
        Given a mocked page
        When `process_individual_page_for_headless_cms_api()`
            is called from an instance of `PrivateAPICrawler`
        Then the call is delegated to the `InternalAPIClient`

        """
        # Given
        mocked_page = mock.Mock()
        spy_internal_api_client: mock.Mock = (
            private_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        private_api_crawler_with_mocked_internal_api_client.process_individual_page_for_headless_cms_api(
            page=mocked_page
        )

        # Then
        spy_internal_api_client.hit_pages_detail_endpoint.assert_called_once_with(
            page_id=mocked_page.id
        )

    def test_process_list_pages_for_headless_cms_api_records_correct_log_(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given an instance of a `PrivateAPICrawler`
        When `process_list_pages_for_headless_cms_api()` is called
        Then the correct logs are recorded
        """
        # Given
        crawler = private_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_list_pages_for_headless_cms_api()

        # Then
        assert "Hitting list GET pages/ endpoint" in caplog.text
        assert "Hitting list GET pages/ endpoint for all page types" in caplog.text

    def test_process_detail_pages_for_headless_cms_api_records_correct_log_(
        self,
        private_api_crawler_with_mocked_internal_api_client: PrivateAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of mocked `Page` objects
        When `process_detail_pages_for_headless_cms_api()`
            is called from an instance of `PrivateAPICrawler`
        Then the correct logs are recorded
        """
        # Given
        mocked_pages = [mock.Mock(title="COVID-19"), mock.Mock(title="Influenza")]
        crawler = private_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_detail_pages_for_headless_cms_api(pages=mocked_pages)

        # Then
        for mocked_page in mocked_pages:
            assert (
                f"Hitting GET pages/ endpoint for `{mocked_page.title}` page"
                in caplog.text
            )
