from unittest import mock

import pytest

from caching.frontend.crawler import FrontEndCrawler

MODULE_PATH = "caching.frontend.crawler"


@pytest.fixture()
def frontend_crawler_with_mocked_internal_api_client() -> FrontEndCrawler:
    return FrontEndCrawler(
        frontend_base_url="http://fake-frontend.co.uk",
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
            headers={"x-cdn-auth": expected_cdn_auth_key},
        )

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    @mock.patch.object(FrontEndCrawler, "_build_url_for_home_page")
    def test_process_page_for_home_page(
        self,
        spy_build_url_for_home_page: mock.MagicMock,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "home.HomePage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_home_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_build_url_for_home_page`: To check the correct
                method is being called to build the URL
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "home.HomePage"}

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        spy_build_url_for_home_page.assert_called_once()
        url_for_home_page = spy_build_url_for_home_page.return_value
        spy_hit_frontend_page.assert_called_once_with(url=url_for_home_page)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    @mock.patch.object(FrontEndCrawler, "_build_url_for_topic_page")
    def test_process_page_for_topic_page(
        self,
        spy_build_url_for_topic_page: mock.MagicMock,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "topic.TopicPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_topic_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_build_url_for_topic_page`: To check the correct
                method is being called to build the URL
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "topic.TopicPage", "slug": "fake-topic-page-slug"}

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        spy_build_url_for_topic_page.assert_called_once_with(slug=page_item["slug"])
        url_for_topic_page = spy_build_url_for_topic_page.return_value
        spy_hit_frontend_page.assert_called_once_with(url=url_for_topic_page)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    @mock.patch.object(FrontEndCrawler, "_build_url_for_common_page")
    def test_process_page_for_common_page(
        self,
        spy_build_url_for_common_page: mock.MagicMock,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page item dict with a key "type" of value "common.CommonPage"
        When `process_page()` is called from an instance of `FrontEndCrawler`
        Then `_build_url_for_common_page()` is called
        And the returned url is passed to the call to `hit_frontend_page()`

        Patches:
            `spy_build_url_for_common_page`: To check the correct
                method is being called to build the URL
            `spy_hit_frontend_page`: For the main assertion,
                to check the request is being made to the correct URL
        """
        # Given
        page_item = {"type": "common.CommonPage", "slug": "fake-common-page-slug"}

        # When
        frontend_crawler_with_mocked_internal_api_client.process_page(
            page_item=page_item
        )

        # Then
        spy_build_url_for_common_page.assert_called_once_with(slug=page_item["slug"])
        url_for_common_page = spy_build_url_for_common_page.return_value
        spy_hit_frontend_page.assert_called_once_with(url=url_for_common_page)

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
    @mock.patch.object(FrontEndCrawler, "_build_url_for_feedback_confirmation_page")
    def test_process_all_pages_hits_frontend_for_feedback_confirmation_page(
        self,
        spy_build_url_for_feedback_confirmation_page: mock.MagicMock,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given no input
        When `process_all_pages()` is called from an instance of `FrontEndCrawler`
        Then `hit_frontend_page()` is called
            with the URL for the feedback confirmation page

        Patches:
            `spy_build_url_for_feedback_confirmation_page`: To isolate the returned URL
            `spy_hit_frontend_page`: For the main assertion

        """
        # Given / When
        frontend_crawler_with_mocked_internal_api_client.process_all_pages()

        # Then
        expected_url = spy_build_url_for_feedback_confirmation_page.return_value
        spy_hit_frontend_page.assert_called_with(url=expected_url)

    # URL construction

    def test_build_url_for_topic_page(
        self, frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler
    ):
        """
        Given a slug for a topic page
        When `_build_url_for_topic_page()` is called from an instance of `FrontEndCrawler`
        Then the correct URL will be returned
        """
        # Given
        topic_page_slug = "influenza"

        # When
        topic_page_url: str = (
            frontend_crawler_with_mocked_internal_api_client._build_url_for_topic_page(
                slug=topic_page_slug
            )
        )

        # Then
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url
        assert topic_page_url == f"{base_url}/topics/{topic_page_slug}"

    def test_build_url_for_common_page(
        self, frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler
    ):
        """
        Given a slug for a common page
        When `_build_url_for_common_page()` is called from an instance of `FrontEndCrawler`
        Then the correct URL will be returned
        """
        # Given
        common_page_slug = "about"

        # When
        common_page_url: str = (
            frontend_crawler_with_mocked_internal_api_client._build_url_for_common_page(
                slug=common_page_slug
            )
        )

        # Then
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url
        assert common_page_url == f"{base_url}/{common_page_slug}"

    def test_build_url_for_home_page(
        self, frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler
    ):
        """
        Given no input
        When `_build_url_for_home_page()` is called from an instance of `FrontEndCrawler`
        Then the correct URL will be returned
        """
        # Given / When
        home_page_url: str = (
            frontend_crawler_with_mocked_internal_api_client._build_url_for_home_page()
        )

        # Then
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url
        assert home_page_url == base_url

    def test_build_url_for_feedback_confirmation_page(
        self, frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler
    ):
        """
        Given no input
        When `_build_url_for_feedback_confirmation_page()` is called
            from an instance of `FrontEndCrawler`
        Then the correct URL will be returned
        """
        # Given / When
        feedback_confirmation_page_url: str = (
            frontend_crawler_with_mocked_internal_api_client._build_url_for_feedback_confirmation_page()
        )

        # Then
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url
        assert feedback_confirmation_page_url == f"{base_url}/feedback/confirmation"
