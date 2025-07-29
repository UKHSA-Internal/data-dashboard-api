from http import HTTPMethod
from unittest import mock

import pytest
from caching.private_api.management import (
    CacheManagement,
    RESERVED_NAMESPACE_KEY_PREFIX,
)


class TestCacheManagementBuildCacheKeyEntryForRequest:
    @pytest.mark.parametrize(
        "endpoint_path, data, expected_data",
        (
            [
                "api/charts/v3/",
                {"key_a": "value_a"},
                # expected dicts should bundle the endpoint path into the dicts
                {"key_a": "value_a", "endpoint_path": "api/charts/v3"},
            ],
            [
                "api/charts/v3",
                {"key_a": "value_a"},
                # expected dicts should treat endpoint paths with trailing `/` chars the same
                {"key_a": "value_a", "endpoint_path": "api/charts/v3"},
            ],
            [
                "api/charts/v3",
                {"key_b": "value_b", "key_a": "value_a"},
                # expected dict should sort key value pairs
                {
                    "key_a": "value_a",
                    "key_b": "value_b",
                    "endpoint_path": "api/charts/v3",
                },
            ],
        ),
    )
    @mock.patch.object(CacheManagement, "create_hash_for_data")
    def test_build_cache_entry_key_for_data(
        self,
        spy_create_hash_for_data: mock.MagicMock,
        endpoint_path: str,
        data: dict[str, str],
        expected_data: dict[str, str],
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given an endpoint path and input data
        When `_build_cache_entry_key_for_data()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to the `create_hash_for_data()` method
        """
        # Given
        endpoint: str = endpoint_path
        input_data: dict = data

        # When
        created_hash = (
            cache_management_with_in_memory_cache._build_cache_entry_key_for_data(
                endpoint_path=endpoint,
                data=input_data,
            )
        )

        # Then
        spy_create_hash_for_data.assert_called_once_with(data=expected_data)
        assert created_hash == spy_create_hash_for_data.return_value

    @mock.patch.object(CacheManagement, "build_cache_entry_key_for_data")
    def test_build_cache_entry_key_for_request_post(
        self,
        spy_build_cache_entry_key_for_data: mock.MagicMock,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked POST request
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to `build_cache_entry_key_for_data()`
            with the correct args
        """
        # Given
        mocked_request = mock.Mock(method="POST")

        # When
        cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
            request=mocked_request,
            is_reserved_namespace=False,
        )

        # Then
        spy_build_cache_entry_key_for_data.assert_called_once_with(
            endpoint_path=mocked_request.path, data=mocked_request.data
        )

    @mock.patch.object(CacheManagement, "build_cache_entry_key_for_data")
    def test_build_cache_entry_key_for_request_get(
        self,
        spy_build_cache_entry_key_for_data: mock.MagicMock,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked GET request
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to `build_cache_entry_key_for_data()`
            with the correct args
        """
        # Given
        mocked_request = mock.MagicMock(method="GET")
        mocked_request.query_params.dict.return_value = {"param_a": "query_a"}

        # When
        cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
            request=mocked_request,
            is_reserved_namespace=False,
        )

        # Then
        spy_build_cache_entry_key_for_data.assert_called_once_with(
            endpoint_path=mocked_request.path, data=mocked_request.query_params.dict()
        )

    @mock.patch.object(CacheManagement, "_build_standalone_key_for_request")
    def test_build_cache_entry_key_for_reserved_namespace_entry(
        self,
        mocked_build_standalone_key_for_request: mock.MagicMock,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked POST request in the reserved namespace
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then cache key is returned with the reserved namespace prefix
        """
        # Given
        mocked_build_standalone_key_for_request.return_value = "some-key"
        mocked_request = mock.Mock(method="POST")

        # When
        cache_key: str = (
            cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
                request=mocked_request,
                is_reserved_namespace=True,
            )
        )

        # Then
        assert cache_key == f"{RESERVED_NAMESPACE_KEY_PREFIX}-some-key"

    @pytest.mark.parametrize(
        "invalid_http_method",
        (
            HTTPMethod.PUT,
            HTTPMethod.PATCH,
            HTTPMethod.DELETE,
            HTTPMethod.HEAD,
            HTTPMethod.CONNECT,
        ),
    )
    def test_build_cache_entry_key_for_request_raises_error_for_invalid_http_method(
        self,
        invalid_http_method: HTTPMethod,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked request of an invalid HTTP method
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then a `ValueError` is raised
        """
        # Given
        mocked_request = mock.MagicMock(method=invalid_http_method.value)

        # When / Then
        with pytest.raises(ValueError):
            cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
                request=mocked_request,
                is_reserved_namespace=False,
            )
