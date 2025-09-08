from unittest import mock

import pytest

from caching.private_api.client import CacheClient, InMemoryCacheClient
from caching.private_api.management import CacheManagement


class TestCacheManagementInit:
    def test_cache_client_can_be_provided_to_init(self):
        """
        Given a pre-existing cache client
        When the `CacheManagement` class is initialized
        Then the `_client` is set with the provided client
        """
        # Given
        mocked_cache_client = mock.Mock()

        # When
        cache_management = CacheManagement(
            client=mocked_cache_client, in_memory=mock.Mock()
        )

        # Then
        assert cache_management._client == mocked_cache_client

    @pytest.mark.parametrize(
        "in_memory, is_reserved_namespace",
        (
            [True, True],
            [True, False],
            [False, True],
            [False, False],
        ),
    )
    @mock.patch.object(CacheManagement, "_create_cache_client")
    def test_create_cache_client_is_delegated_to_during_init_when_client_not_provided(
        self,
        spy_create_cache_client: mock.MagicMock,
        in_memory: bool,
        is_reserved_namespace: bool,
    ):
        """
        Given no pre-existing cache client
        When the `CacheManagement` class is initialized
        Then the call is delegated to the `_create_cache_client()` method
        """
        # Given / When
        cache_management = CacheManagement(
            in_memory=in_memory, is_reserved_namespace=is_reserved_namespace
        )

        # Then
        assert cache_management._client == spy_create_cache_client.return_value
        spy_create_cache_client.assert_called_once_with(
            in_memory=in_memory, is_reserved_namespace=is_reserved_namespace
        )

    @pytest.mark.parametrize(
        "in_memory, expected_client_class",
        ([True, InMemoryCacheClient], [False, CacheClient]),
    )
    def test_create_cache_client_returns_correct_cache_client(
        self, in_memory: bool, expected_client_class: CacheClient
    ):
        """
        Given a boolean for the `in_memory` parameter
        When `_create_cache_client()` is called
            from an instance of `CacheManagement`
        Then the correct `CacheClient` object is returned
        """
        # Given
        cache_management = CacheManagement(in_memory=mock.Mock())

        # When
        created_cache_client = cache_management._create_cache_client(
            in_memory=in_memory
        )

        # Then
        assert isinstance(created_cache_client, expected_client_class)
