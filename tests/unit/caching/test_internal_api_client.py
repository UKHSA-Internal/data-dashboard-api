from unittest import mock

import pytest
from rest_framework.test import APIClient

from caching.internal_api_client import (
    CACHE_CHECK_HEADER_KEY,
    CACHE_FORCE_REFRESH_HEADER_KEY,
    PAGE_TYPES,
    InternalAPIClient,
)
from metrics.data.managers.api_keys import CustomAPIKeyManager


class FakeAPIKeyManager(CustomAPIKeyManager):
    @staticmethod
    def create_key(name: str) -> tuple[mock.Mock, str]:
        created_api_key = mock.Mock()
        created_api_key.name = name

        return created_api_key, "abc123"


class TestInternalAPIClient:
    # Constructor tests
    @pytest.mark.parametrize(
        "attribute_on_class, expected_path",
        (
            [
                ("pages_endpoint_path", "/api/pages/"),
                ("headlines_endpoint_path", "/api/headlines/v2/"),
                ("trends_endpoint_path", "/api/trends/v2/"),
                ("charts_endpoint_path", "/api/charts/v3/"),
                ("tables_endpoint_path", "/api/tables/v4/"),
                ("downloads_endpoint_path", "/api/downloads/v2/"),
            ]
        ),
    )
    def test_default_endpoint_paths_are_set_on_initialization(
        self, attribute_on_class: str, expected_path: str
    ):
        """
        Given an instance of the `InternalAPIClient`
        When the default endpoint_paths are retrieved
        Then the correct endpoint path is returned
        """
        # Given
        internal_api_client = InternalAPIClient(client=mock.Mock())

        # When
        retrieved_endpoint_path = getattr(internal_api_client, attribute_on_class)

        # Then
        assert retrieved_endpoint_path == expected_path

    def test_client_can_be_provided_to_init(self):
        """
        Given a mocked pre-defined client
        When an instance of the `InternalAPIClient` is created
        Then the internal `_client` is set with the provided client object
        """
        # Given
        mocked_client = mock.Mock()

        # When
        internal_api_client = InternalAPIClient(client=mocked_client)

        # Then
        assert internal_api_client._client == mocked_client

    @mock.patch.object(InternalAPIClient, "create_api_client")
    def test_create_api_client_is_called_when_not_provided(self, spy_create_api_client):
        """
        Given an instance of the `InternalAPIClient`
            which has not been provided with an API client
        When the `InternalAPIClient` is initialized
        Then the `create_api_client()` method is called

        Patches:
            `spy_create_api_client`: For the main assertion
        """
        # Given / When
        internal_api_client = InternalAPIClient()

        # Then
        spy_create_api_client.assert_called_once()
        assert internal_api_client._client == spy_create_api_client.return_value

    def test_force_refresh_attribute_defaults_to_false(self):
        """
        Given no provided argument for `force_refresh`
        When the `InternalAPIClient` class is initialized
        Then the `force_refresh` attribute is set to False
        """
        # Given
        mocked_client = mock.Mock()

        # When
        internal_api_client = InternalAPIClient(client=mocked_client)

        # Then
        assert not internal_api_client.force_refresh

    def test_cache_check_only_attribute_defaults_to_false(self):
        """
        Given no provided argument for `cache_check_only`
        When the `InternalAPIClient` class is initialized
        Then the `cache_check_only` attribute is set to False
        """
        # Given
        mocked_client = mock.Mock()

        # When
        internal_api_client = InternalAPIClient(client=mocked_client)

        # Then
        assert not internal_api_client.cache_check_only

    # API key manager & API client tests

    def test_create_api_client_returns_api_client(self):
        """
        Given an instance of the `InternalAPIClient`
        When `create_api_client()` is called from the `InternalAPIClient`
        Then an instance of the `APIClient` is returned
        And an API key has been created and set on the authorization of the client
        """
        # Given
        internal_api_client = InternalAPIClient(client=mock.Mock())

        # When
        created_api_client = internal_api_client.create_api_client()

        # Then
        assert isinstance(created_api_client, APIClient)

    # Header construction tests

    @pytest.mark.parametrize(
        "force_refresh, cache_check_only",
        (
            [True, True],
            [True, False],
            [False, True],
            [False, False],
        ),
    )
    def test_build_headers(self, force_refresh: bool, cache_check_only: bool):
        """
        Given provided `force_refresh` and `cache_check_only` values
        When `build_headers()` is called
            from an instance of `InternalAPIClient`
        Then the correct dict representing the headers is returned
        """
        # Given
        mocked_client = mock.Mock()
        internal_api_client = InternalAPIClient(
            client=mocked_client,
            force_refresh=force_refresh,
            cache_check_only=cache_check_only,
        )

        # When
        headers = internal_api_client.build_headers()

        # Then
        expected_headers = {
            CACHE_FORCE_REFRESH_HEADER_KEY: force_refresh,
            CACHE_CHECK_HEADER_KEY: cache_check_only,
        }
        assert headers == expected_headers

    # Endpoint calls tests

    def test_hit_headlines_endpoint_delegates_call_correctly(self):
        """
        Given a client and mocked request data
        When `hit_headlines_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_headlines_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.get.return_value
        mocked_client.get.assert_called_once_with(
            path=internal_api_client.headlines_endpoint_path,
            headers=internal_api_client.build_headers(),
            data=mocked_request_data,
        )

    def test_hit_trends_endpoint_delegates_call_correctly(self):
        """
        Given a client and mocked request data
        When `hit_trends_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_trends_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.get.return_value
        mocked_client.get.assert_called_once_with(
            path=internal_api_client.trends_endpoint_path,
            headers=internal_api_client.build_headers(),
            data=mocked_request_data,
        )

    def test_hit_charts_endpoint_delegates_call_correctly(self):
        """
        Given a client and mocked request data
        When `hit_charts_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_charts_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.post.return_value
        mocked_client.post.assert_called_once_with(
            path=internal_api_client.charts_endpoint_path,
            data=mocked_request_data,
            headers=internal_api_client.build_headers(),
            format="json",
        )

    def test_hit_tables_endpoint_delegates_calls_correctly(self):
        """
        Given a client and mocked request data
        When `hit_tables_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_tables_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.post.return_value
        expected_headers = internal_api_client.build_headers()
        mocked_client.post.assert_called_once_with(
            path=internal_api_client.tables_endpoint_path,
            data=mocked_request_data,
            headers=expected_headers,
            format="json",
        )

    def test_hit_downloads_endpoint_delegates_call_correctly(self):
        """
        Given a client and mocked request data
        When `hit_downloads_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_downloads_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.post.return_value
        mocked_client.post.assert_called_once_with(
            path=internal_api_client.downloads_endpoint_path,
            data=mocked_request_data,
            headers=internal_api_client.build_headers(),
            format="json",
        )

    def test_hit_pages_list_endpoint_delegates_call_correctly(self):
        """
        Given a client
        When `hit_pages_list_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_pages_list_endpoint()

        # Then
        assert response == internal_api_client._client.get.return_value
        mocked_client.get.assert_called_once_with(
            path=internal_api_client.pages_endpoint_path,
            headers=internal_api_client.build_headers(),
            format="json",
        )

    @pytest.mark.parametrize(
        "page_type_query_param",
        ["common.CommonPage", "topic.TopicPage", "home.HomePage"],
    )
    def test_hit_pages_list_endpoint_for_page_type_query_param_delegates_call_correctly(
        self, page_type_query_param: str
    ):
        """
        Given a client
        When `hit_pages_list_endpoint_for_page_type_query_param()`
            is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = (
            internal_api_client.hit_pages_list_endpoint_for_page_type_query_param(
                page_type_query_param=page_type_query_param
            )
        )

        # Then
        assert response == internal_api_client._client.get.return_value
        mocked_client.get.assert_called_with(
            path=internal_api_client.pages_endpoint_path,
            headers=internal_api_client.build_headers(),
            data={"type": page_type_query_param},
            format="json",
        )

    @mock.patch.object(
        InternalAPIClient, "hit_pages_list_endpoint_for_page_type_query_param"
    )
    def test_hit_pages_list_endpoint_for_all_page_types_delegates_call_correctly(
        self, spy_hit_pages_list_endpoint_for_page_type_query_param: mock.MagicMock
    ):
        """
        Given a client
        When `hit_pages_list_endpoint_for_all_page_types()`
            is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object

        Patches:
            `spy_hit_pages_list_endpoint_for_page_type_query_param`: For the
                main assertion, to check each page type query param is processed
        """
        # Given
        mocked_client = mock.Mock()
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        internal_api_client.hit_pages_list_endpoint_for_all_page_types()

        # Then
        expected_calls = [
            mock.call(page_type_query_param=page_type) for page_type in PAGE_TYPES
        ]
        spy_hit_pages_list_endpoint_for_page_type_query_param.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    def test_hit_pages_detail_endpoint_delegates_call_correctly(self):
        """
        Given a client and an ID for a given page
        When `hit_pages_detail_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        fake_page_id = 123
        internal_api_client = InternalAPIClient(client=mocked_client)

        # When
        response = internal_api_client.hit_pages_detail_endpoint(page_id=fake_page_id)

        # Then
        assert response == internal_api_client._client.get.return_value
        expected_path = f"{internal_api_client.pages_endpoint_path}{fake_page_id}"

        expected_calls = [
            mock.call(
                path=expected_path,
                headers=internal_api_client.build_headers(),
                format="json",
            ),
            mock.call(
                path=f"{expected_path}/",
                headers=internal_api_client.build_headers(),
                format="json",
            ),
        ]

        mocked_client.get.assert_has_calls(calls=expected_calls, any_order=True)
