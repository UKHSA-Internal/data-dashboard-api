from unittest import mock

import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from caching.internal_api_client import (
    CACHE_CHECK_HEADER_KEY,
    CACHE_FORCE_REFRESH_HEADER_KEY,
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
                ("tables_endpoint_path", "/api/tables/v3/"),
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
        internal_api_client = InternalAPIClient(
            client=mock.Mock(), api_key_manager=mock.Mock()
        )

        # When
        retrieved_endpoint_path = getattr(internal_api_client, attribute_on_class)

        # Then
        assert retrieved_endpoint_path == expected_path

    def test_key_manager_can_be_provided_to_init(self):
        """
        Given a mocked pre-defined api key manager
        When an instance of the `InternalAPIClient` is created
        Then the internal `_api_key_manager` is set with the provided client object
        """
        # Given
        mocked_key_manager = mock.Mock()

        # When
        internal_api_client = InternalAPIClient(
            client=mock.Mock(), api_key_manager=mocked_key_manager
        )

        # Then
        assert internal_api_client._api_key_manager == mocked_key_manager

    def test_client_can_be_provided_to_init(self):
        """
        Given a mocked pre-defined client
        When an instance of the `InternalAPIClient` is created
        Then the internal `_client` is set with the provided client object
        """
        # Given
        mocked_client = mock.Mock()

        # When
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

        # Then
        assert internal_api_client._client == mocked_client

    @mock.patch.object(InternalAPIClient, "create_api_key_manager")
    def test_create_api_key_manager_is_called_when_not_provided(
        self, spy_create_api_key_manager
    ):
        """
        Given an instance of the `InternalAPIClient`
            which has not been provided with an API key manager
        When the `InternalAPIClient` is initialized
        Then the `create_api_key_manager()` method is called

        Patches:
            `spy_create_api_key_manager`: For the main assertion

        """
        # Given / When
        internal_api_client = InternalAPIClient(client=mock.Mock())

        # Then
        spy_create_api_key_manager.assert_called_once()
        assert (
            internal_api_client._api_key_manager
            == spy_create_api_key_manager.return_value
        )

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
        internal_api_client = InternalAPIClient(api_key_manager=mock.Mock())

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

    def test_create_api_key_manager(self):
        """
        Given an instance of the `InternalAPIClient`
        When `create_api_key_manager()` is called from the `InternalAPIClient`
        Then an instance of the `CustomAPIKeyManager` is returned
        """
        # Given
        internal_api_client = InternalAPIClient(
            client=mock.Mock(), api_key_manager=mock.Mock()
        )

        # When
        created_api_key_manager = internal_api_client.create_api_key_manager()

        # Then
        assert isinstance(created_api_key_manager, CustomAPIKeyManager)
        assert created_api_key_manager.model == APIKey

    def test_create_api_client_returns_api_client(self):
        """
        Given an instance of the `InternalAPIClient`
        When `create_api_client()` is called from the `InternalAPIClient`
        Then an instance of the `APIClient` is returned
        And an API key has been created and set on the authorization of the client
        """
        # Given
        internal_api_client = InternalAPIClient(
            client=mock.Mock(), api_key_manager=FakeAPIKeyManager()
        )

        # When
        created_api_client = internal_api_client.create_api_client()

        # Then
        assert isinstance(created_api_client, APIClient)

    @mock.patch.object(APIClient, "credentials")
    def test_create_api_client_sets_api_key_on_client(
        self, spy_credentials: mock.MagicMock
    ):
        """
        Given an instance of the `InternalAPIClient`
        When `create_api_client()` is called from the `InternalAPIClient`
        Then a new API key is created and set on the authorization of the client
        """
        # Given
        mocked_api_key_manager = mock.Mock()
        fake_expected_api_key_for_header = "abc"
        mocked_api_key_manager.create_key.return_value = (
            mock.Mock(),
            fake_expected_api_key_for_header,
        )
        internal_api_client = InternalAPIClient(
            client=mock.Mock(), api_key_manager=mocked_api_key_manager
        )

        # When
        internal_api_client.create_api_client()

        # Then
        mocked_api_key_manager.create_key.assert_called_once_with(
            name=internal_api_client.temporary_api_key_name
        )
        spy_credentials.assert_called_once_with(
            HTTP_AUTHORIZATION=fake_expected_api_key_for_header
        )

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
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

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
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

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
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

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

    def test_hit_tables_endpoint_delegates_call_correctly(self):
        """
        Given a client and mocked request data
        When `hit_tables_endpoint()` is called from an instance of the `InternalAPIClient`
        Then the call is delegated to the `client` object
        """
        # Given
        mocked_client = mock.Mock()
        mocked_request_data = mock.Mock()
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

        # When
        response = internal_api_client.hit_tables_endpoint(data=mocked_request_data)

        # Then
        assert response == internal_api_client._client.post.return_value
        mocked_client.post.assert_called_once_with(
            path=internal_api_client.tables_endpoint_path,
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
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

        # When
        response = internal_api_client.hit_pages_list_endpoint()

        # Then
        assert response == internal_api_client._client.get.return_value
        mocked_client.get.assert_called_once_with(
            path=internal_api_client.pages_endpoint_path,
            headers=internal_api_client.build_headers(),
            format="json",
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
        internal_api_client = InternalAPIClient(
            client=mocked_client, api_key_manager=mock.Mock()
        )

        # When
        response = internal_api_client.hit_pages_detail_endpoint(page_id=fake_page_id)

        # Then
        assert response == internal_api_client._client.get.return_value
        expected_path = f"{internal_api_client.pages_endpoint_path}{fake_page_id}"
        mocked_client.get.assert_called_once_with(
            path=expected_path,
            headers=internal_api_client.build_headers(),
            format="json",
        )
