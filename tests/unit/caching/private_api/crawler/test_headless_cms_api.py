from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler.headless_cms_api import HeadlessCMSAPICrawler
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


@pytest.fixture
def headless_cms_api_crawler_with_mocked_internal_api_client() -> HeadlessCMSAPICrawler:
    return HeadlessCMSAPICrawler(internal_api_client=mock.Mock())


class TestHeadlessCMSAPICrawler:
    def test_process_list_pages_for_headless_cms_api_delegates_call_to_api_client(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given a mocked `InternalAPIClient`
        When `process_list_pages_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
        Then the call is delegated to the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client: mock.Mock = (
            headless_cms_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        headless_cms_api_crawler_with_mocked_internal_api_client.process_list_pages_for_headless_cms_api()

        # Then
        spy_internal_api_client.hit_pages_list_endpoint.assert_called_once()
        spy_internal_api_client.hit_pages_list_endpoint_for_all_page_types.assert_called_once()

    @mock.patch.object(
        HeadlessCMSAPICrawler, "process_individual_page_for_headless_cms_api"
    )
    def test_process_detail_pages_for_headless_cms_api_delegates_call_for_each_page(
        self,
        spy_process_individual_page_for_headless_cms_api: mock.MagicMock,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given a number of pages
        When `process_detail_pages_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
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
        headless_cms_api_crawler_with_mocked_internal_api_client.process_detail_pages_for_headless_cms_api(
            pages=pages
        )

        # Then
        expected_calls = [mock.call(page=page) for page in pages]
        spy_process_individual_page_for_headless_cms_api.assert_has_calls(
            calls=expected_calls
        )

    def test_process_individual_page_for_headless_cms_api_delegates_call_to_api_client(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given a mocked page
        When `process_individual_page_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
        Then the call is delegated to the `InternalAPIClient`
        """
        # Given
        mocked_page = mock.Mock()
        spy_internal_api_client: mock.Mock = (
            headless_cms_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        headless_cms_api_crawler_with_mocked_internal_api_client.process_individual_page_for_headless_cms_api(
            page=mocked_page
        )

        # Then
        spy_internal_api_client.hit_pages_detail_endpoint.assert_called_once_with(
            page_id=mocked_page.id
        )

    def test_process_list_pages_for_headless_cms_api_records_correct_log(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given an instance of a `HeadlessCMSAPICrawler`
        When `process_list_pages_for_headless_cms_api()` is called
        Then the correct logs are recorded
        """
        # Given
        crawler = headless_cms_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_list_pages_for_headless_cms_api()

        # Then
        assert "Hitting list GET pages/ endpoint" in caplog.text
        assert "Hitting list GET pages/ endpoint for all page types" in caplog.text

    def test_process_detail_pages_for_headless_cms_api_records_correct_log(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a list of mocked `Page` objects
        When `process_detail_pages_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
        Then the correct logs are recorded
        """
        # Given
        mocked_pages = [mock.Mock(title="COVID-19"), mock.Mock(title="Influenza")]
        crawler = headless_cms_api_crawler_with_mocked_internal_api_client

        # When
        crawler.process_detail_pages_for_headless_cms_api(pages=mocked_pages)

        # Then
        for mocked_page in mocked_pages:
            assert (
                f"Hitting GET pages/ endpoint for `{mocked_page.title}` page"
                in caplog.text
            )

    # Snippets

    @mock.patch.object(
        HeadlessCMSAPICrawler, "process_global_banners_for_headless_cms_api"
    )
    @mock.patch.object(HeadlessCMSAPICrawler, "process_menus_for_headless_cms_api")
    def test_process_all_snippets(
        self,
        spy_process_global_banners_for_headless_cms_api: mock.MagicMock,
        spy_process_menus_for_headless_cms_api: mock.MagicMock,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given no input
        When `process_all_snippets()` is called
            from an instance of the `HeadlessCMSAPICrawler`
        Then the call is delegated to each of the methods
            for the correct snippets
        """
        # Given / When
        headless_cms_api_crawler_with_mocked_internal_api_client.process_all_snippets()

        # Then
        spy_process_global_banners_for_headless_cms_api.assert_called_once()
        spy_process_menus_for_headless_cms_api.assert_called_once()

    def test_process_global_banners_for_headless_cms_api_delegates_call_to_api_client(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given no input
        When `process_global_banners_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
        Then the call is delegated to the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client: mock.Mock = (
            headless_cms_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        headless_cms_api_crawler_with_mocked_internal_api_client.process_global_banners_for_headless_cms_api()

        # Then
        spy_internal_api_client.hit_global_banners_endpoint.assert_called_once()

    def test_process_menus_for_headless_cms_api_delegates_call_to_api_client(
        self,
        headless_cms_api_crawler_with_mocked_internal_api_client: HeadlessCMSAPICrawler,
    ):
        """
        Given no input
        When `process_menus_for_headless_cms_api()`
            is called from an instance of `HeadlessCMSAPICrawler`
        Then the call is delegated to the `InternalAPIClient`
        """
        # Given
        spy_internal_api_client: mock.Mock = (
            headless_cms_api_crawler_with_mocked_internal_api_client._internal_api_client
        )

        # When
        headless_cms_api_crawler_with_mocked_internal_api_client.process_menus_for_headless_cms_api()

        # Then
        spy_internal_api_client.hit_menus_endpoint.assert_called_once()
