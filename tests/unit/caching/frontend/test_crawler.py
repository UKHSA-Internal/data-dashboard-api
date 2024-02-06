from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from caching.common.geographies_crawler import GeographyData
from caching.frontend.crawler import DEFAULT_REQUEST_TIMEOUT, FrontEndCrawler

MODULE_PATH = "caching.frontend.crawler"


@pytest.fixture()
def frontend_crawler_with_mocked_internal_api_client() -> FrontEndCrawler:
    return FrontEndCrawler(
        frontend_base_url="https://fake-frontend.co.uk",
        cdn_auth_key="123456789",
        internal_api_client=mock.MagicMock(),
    )


class TestFrontEndCrawler:
    # Private API/headless CMS API

    def test_get_all_page_items_from_api(
        self, frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler
    ):
        """
        Given a mocked `InternalAPIClient`
        When `get_all_page_items_from_api()` is called from an instance of `FrontEndCrawler`
        Then the correct page items are returned from the response
        """
        # Given
        expected_mocked_page_items = mock.Mock()
        page_response_data = {"items": expected_mocked_page_items}
        mocked_internal_api_client = (
            frontend_crawler_with_mocked_internal_api_client._internal_api_client
        )
        mocked_internal_api_client.hit_pages_list_endpoint.return_value.json.return_value = (
            page_response_data
        )

        # When
        returned_page_items = (
            frontend_crawler_with_mocked_internal_api_client.get_all_page_items_from_api()
        )

        # Then
        assert returned_page_items == expected_mocked_page_items

    # Frontend requests

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_frontend_page(
        self,
        spy_requests: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a URL
        When `hit_frontend_page()` is called from an instance of `FrontEndCrawler`
        Then a GET request is sent to the URL with the correct headers
        """
        # Given
        url = "https://fake-url.com"

        # When
        frontend_crawler_with_mocked_internal_api_client.hit_frontend_page(url=url)

        # Then
        expected_cdn_auth_key = (
            f'"{frontend_crawler_with_mocked_internal_api_client._cdn_auth_key}"'
        )
        spy_requests.get.assert_called_once_with(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={"x-cdn-auth": expected_cdn_auth_key},
            params=None,
        )

        assert f"Processed `{url}`" in caplog.text

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_frontend_page_with_query_params(
        self,
        spy_requests: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a URL and a dict for the query parameters
        When `hit_frontend_page()` is called from an instance of `FrontEndCrawler`
        Then a GET request is sent to the URL with the correct headers
        """
        # Given
        url = "https://fake-url.com"
        query_params = {"areaType": "Lower Tier Local Authority", "areaName": "London"}

        # When
        frontend_crawler_with_mocked_internal_api_client.hit_frontend_page(
            url=url, params=query_params
        )

        # Then
        expected_cdn_auth_key = (
            f'"{frontend_crawler_with_mocked_internal_api_client._cdn_auth_key}"'
        )
        spy_requests.get.assert_called_once_with(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={"x-cdn-auth": expected_cdn_auth_key},
            params=query_params,
        )

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_home_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "home.HomePage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_home_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "home.HomePage"}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        expected_home_page_url: str = frontend_url_builder.build_url_for_home_page()
        spy_hit_frontend_page.assert_called_once_with(url=expected_home_page_url)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_topic_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "topic.TopicPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_topic_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "topic.TopicPage", "slug": "fake-topic-page-slug"}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_topic_page: str = frontend_url_builder.build_url_for_topic_page(
            slug=page_item["slug"]
        )
        spy_hit_frontend_page.assert_called_once_with(url=url_for_topic_page)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_common_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "common.CommonPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_common_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "common.CommonPage", "slug": "fake-common-page-slug"}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_common_page: str = frontend_url_builder.build_url_for_common_page(
            slug=page_item["slug"]
        )
        spy_hit_frontend_page.assert_called_once_with(url=url_for_common_page)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_whats_new_parent_page_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type"
            of value "whats_new.WhatsNewParentPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_whats_new_parent_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "whats_new.WhatsNewParentPage"}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_whats_new_parent_page: str = (
            frontend_url_builder.build_url_for_whats_new_parent_page()
        )
        spy_hit_frontend_page.assert_called_once_with(url=url_for_whats_new_parent_page)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_whats_new_child_entry_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type"
            of value "whats_new.WhatsNewChildEntry"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_whats_new_child_entry()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        slug = "issue-with-vaccination-data"
        page_item = {"type": "whats_new.WhatsNewChildEntry", "slug": slug}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_whats_new_child_entry: str = (
            frontend_url_builder.build_url_for_whats_new_child_entry(slug=slug)
        )
        spy_hit_frontend_page.assert_called_once_with(url=url_for_whats_new_child_entry)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_metrics_documentation_parent_page_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type"
            of value "metrics_documentation.MetricsDocumentationParentPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `build_url_for_metrics_documentation_parent_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "metrics_documentation.MetricsDocumentationParentPage"}
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_metrics_documentation_page: str = (
            frontend_url_builder.build_url_for_metrics_documentation_parent_page()
        )
        spy_hit_frontend_page.assert_called_once_with(
            url=url_for_metrics_documentation_page
        )

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_metrics_documentation_child_entry_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type"
            of value "metrics_documentation.MetricsDocumentationChildEntry"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `build_url_for_metrics_documentation_child_entry()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        slug = "issue-with-vaccination-data"
        page_item = {
            "type": "metrics_documentation.MetricsDocumentationChildEntry",
            "slug": slug,
        }
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        url_for_metrics_documentation_child_entry: str = (
            frontend_url_builder.build_url_for_metrics_documentation_child_entry(
                slug=slug
            )
        )
        spy_hit_frontend_page.assert_called_once_with(
            url=url_for_metrics_documentation_child_entry
        )

    @pytest.mark.parametrize("page_type", ["", None, "wagtailcore.Page"])
    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_page_for_any_other_page_type(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        page_type: str,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of an invalid value
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then the `hit_frontend_page()` call is not made

        Patches:
            `spy_hit_frontend_page`: For the main assertion,
                to check no request is made
        """
        # Given
        page_item = {"type": page_type}

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        spy_hit_frontend_page.assert_not_called()

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    @mock.patch.object(FrontEndCrawler, "process_page")
    @mock.patch.object(FrontEndCrawler, "get_all_page_items_from_api")
    def test_process_all_pages(
        self,
        mocked_get_all_page_items_from_api: mock.MagicMock,
        spy_process_page: mock.MagicMock,
        mocked_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given no input
        When `process_all_pages()` is called from an instance of `FrontEndCrawler`
        Then `process_page()` is called for each returned page item

        Patches:
            `mocked_get_all_page_items_from_api`: To isolate the returned page items
            `spy_process_page`: For the main assertions
            `mocked_hit_frontend_page:` To remove the side effects of
                having to make a network call

        """
        # Given
        mocked_page_items = [mock.Mock()] * 3
        mocked_get_all_page_items_from_api.return_value = [
            {"meta": p} for p in mocked_page_items
        ]

        # When
        frontend_crawler_with_mocked_internal_api_client.process_all_pages()

        # Then
        expected_calls = [
            mock.call(page_item=mocked_page_item)
            for mocked_page_item in mocked_page_items
        ]
        spy_process_page.assert_has_calls(calls=expected_calls, any_order=True)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_all_pages_hits_frontend_for_feedback_confirmation_page(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given no input
        When `process_all_pages()` is called from an instance of `FrontEndCrawler`
        Then `hit_frontend_page()` is called
            with the URL for the feedback confirmation page

        Patches:
            `spy_hit_frontend_page`: For the main assertion

        """
        # Given
        frontend_url_builder = (
            frontend_crawler_with_mocked_internal_api_client._url_builder
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_all_pages()

        # Then
        expected_url = frontend_url_builder.build_url_for_feedback_confirmation_page()
        spy_hit_frontend_page.assert_called_with(url=expected_url)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_geography_page_combination(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a page slug and an enriched `GeographyData` model
        When `process_geography_page_combination()` is called
            from an instance of the `FrontEndCrawler`
        Then the call is delegated to the `hit_frontend_page()` method
            with the correct URL and query parameters dict

        Patches:
            `spy_hit_frontend_page`: For the main assertion

        """
        # Given
        slug = "covid-19"
        mocked_page = mock.Mock(slug=slug)
        geography_data = GeographyData(
            name="London", geography_type_name="Lower Tier Local Authority"
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_geography_page_combination(
            geography_data=geography_data,
            page=mocked_page,
        )

        # Then
        expected_url = f"{frontend_crawler_with_mocked_internal_api_client._frontend_base_url}/topics/{slug}"
        expected_params = {
            "areaType": "Lower+Tier+Local+Authority",
            "areaName": "London",
        }
        spy_hit_frontend_page.assert_called_once_with(
            url=expected_url,
            params=expected_params,
        )

        expected_log = (
            f"Hitting area selector URL for "
            f"`{frontend_crawler_with_mocked_internal_api_client._frontend_base_url}/topics/{slug}` "
            f"for {geography_data.geography_type_name}:{geography_data.name}"
        )
        assert expected_log in caplog.text
