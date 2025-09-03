from unittest import mock

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from caching.private_api.client import InMemoryCacheClient
from caching.private_api.management import (
    CacheManagement,
    CacheMissError,
    RESERVED_NAMESPACE_KEY_PREFIX,
    RESERVED_NAMESPACE_STAGING_KEY_PREFIX,
    CacheKey,
)


class TestCacheManagementCRUDOperations:
    def test_retrieve_item_from_cache_delegates_call_to_client(self):
        """
        Given a cache entry key
        When `retrieve_item_from_cache()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to the `get()` method on the underlying client
        """
        # Given
        mocked_cache_client = mock.Mock()
        cache_management = CacheManagement(client=mocked_cache_client, in_memory=True)
        fake_cache_entry_key = "abc123"

        # When
        retrieved_response = cache_management.retrieve_item_from_cache(
            cache_entry_key=fake_cache_entry_key
        )

        # Then
        assert retrieved_response == mocked_cache_client.get.return_value

    def test_retrieve_item_from_cache_for_in_memory_cache(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given an in-memory cache which contains a response
        When `retrieve_item_from_cache()` is called
            from an instance of `CacheManagement`
        Then the expected response is returned
        """
        # Given
        fake_cache_entry_key = "abc123"
        expected_mocked_response = mock.Mock()
        # Set the underlying in memory cache with the response we expect to be able to retrieve
        cache_management_with_in_memory_cache._client._cache = {
            fake_cache_entry_key: expected_mocked_response
        }

        # When
        retrieved_response = (
            cache_management_with_in_memory_cache.retrieve_item_from_cache(
                cache_entry_key=fake_cache_entry_key
            )
        )

        # Then
        assert retrieved_response == expected_mocked_response

    def test_retrieve_item_from_cache_raises_error_for_non_existent_entry(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given an in-memory cache which does not contain a given key
        When `retrieve_item_from_cache()` is called
            from an instance of `CacheManagement`
        Then a `CacheMissError` is raised
        """
        # Given
        fake_cache_entry_key = "abc123"
        # Set the underlying in memory cache to be empty
        cache_management_with_in_memory_cache._client._cache = {}

        # When
        with pytest.raises(CacheMissError):
            cache_management_with_in_memory_cache.retrieve_item_from_cache(
                cache_entry_key=fake_cache_entry_key
            )

    # Tests for saving items via the cache client

    @mock.patch.object(CacheManagement, "_render_response")
    def test_save_item_in_cache_delegates_call_to_client(
        self, spy_render_response: mock.MagicMock
    ):
        """
        Given a cache entry key and a response
        When `save_item_in_cache()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to the `put()` method on the underlying client
        """
        # Given
        mocked_cache_client = mock.Mock()
        mocked_response = mock.Mock()
        cache_management = CacheManagement(client=mocked_cache_client, in_memory=True)
        fake_cache_entry_key = "abc123"

        # When
        saved_response = cache_management.save_item_in_cache(
            cache_entry_key=fake_cache_entry_key, item=mocked_response, timeout=123
        )

        # Then
        assert saved_response == spy_render_response.return_value
        spy_render_response.assert_called_once_with(response=mocked_response)

        expected_calls = [
            mock.call(
                cache_entry_key=fake_cache_entry_key,
                value=spy_render_response.return_value,
                timeout=123,
            )
        ]
        assert mocked_cache_client.put.mock_calls == expected_calls

    def test_save_item_in_cache_with_in_memory_cache(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given a cache entry key and a response
        When `save_item_in_cache()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to the `put()` method on the underlying client
        """
        # Given
        mocked_response = mock.Mock(headers={"Content-Type": "application/json"})
        fake_cache_entry_key = "abc123"

        # When
        cache_management_with_in_memory_cache.save_item_in_cache(
            cache_entry_key=fake_cache_entry_key, item=mocked_response, timeout=None
        )

        # Then
        assert (
            fake_cache_entry_key in cache_management_with_in_memory_cache._client._cache
        )

    def test_render_response_sets_correct_json_renderer_on_response(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given a `Response` object
        When `_render_response()` is called from an instance of `CacheManagement`
        Then the returned response has been set with the correct JSON renderer
        """
        # Given
        fake_response = Response()

        # When
        rendered_response = cache_management_with_in_memory_cache._render_response(
            response=fake_response
        )

        # Then
        assert isinstance(rendered_response.accepted_renderer, JSONRenderer)
        assert rendered_response.accepted_media_type == "application/json"
        assert rendered_response.renderer_context == {"response": rendered_response}

    def test_render_response_calls_render(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given a mocked `Response`
        When `_render_response()` is called from an instance of `CacheManagement`
        Then `render()` is called on the response
        """
        # Given
        spy_response = mock.Mock(headers={"Content-Type": "application/json"})

        # When
        rendered_response = cache_management_with_in_memory_cache._render_response(
            response=spy_response
        )

        # Then
        spy_response.render.assert_called_once()
        assert rendered_response == spy_response

    def test_render_response_does_not_call_render_on_csv_responses(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given a mocked `Response` which is content type csv
        When `_render_response()` is called from an instance of `CacheManagement`
        Then `render()` is not called on the response
        """
        # Given
        fake_headers = {"Content-Type": "text/csv"}
        spy_response = mock.Mock(headers=fake_headers)

        # When
        rendered_response = cache_management_with_in_memory_cache._render_response(
            response=spy_response
        )

        # Then
        spy_response.render.assert_not_called()
        assert spy_response.accepted_media_type != "application/json"
        assert rendered_response == spy_response

    # Test to save and then retrieve an item from an in-memory cache

    def test_save_and_retrieve_item_from_cache(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given a cache entry key and a response
        When `save_response_in_cache()` is called
            from an instance of `CacheManagement`
        Then the response can then be retrieved
            by calling `retrieve_response_from_cache()`
        """
        # Given
        mocked_item = mock.Mock(headers={"Content-Type": "application/json"})
        fake_cache_entry_key = "abc"

        # When
        cache_management_with_in_memory_cache.save_item_in_cache(
            cache_entry_key=fake_cache_entry_key, item=mocked_item, timeout=None
        )

        # Then
        retrieved_response = (
            cache_management_with_in_memory_cache.retrieve_item_from_cache(
                cache_entry_key=fake_cache_entry_key
            )
        )
        assert retrieved_response == mocked_item

    def test_clear(self):
        """
        Given an instance of `CacheManagement`
        When `clear()` is called from the object
        Then the call is delegated to the underlying client
        """
        # Given
        spy_client = mock.Mock()

        cache_management = CacheManagement(
            in_memory=True,
            client=spy_client,
            reserved_namespace_key_prefix="ns2",
        )

        # When
        cache_management.clear()

        # Then
        spy_client.clear.assert_called_once()

    def test_delete_many(self):
        """
        Given a list of keys
        When `delete_many()` is called from
            a `CacheManagement` instance
        Then the call is delegated to the underlying client
        """
        # Given
        spy_client = mock.Mock()
        cache_management = CacheManagement(in_memory=True, client=spy_client)
        keys = ["abc", "123", "456"]

        # When
        cache_management.delete_many(keys=keys)

        # Then
        spy_client.delete_many.assert_called_once_with(keys=keys)

    def test_get_all_cache_keys(self):
        """
        Given an `InMemoryCacheClient`
        When `_get_all_cache_keys()` is called
            from the `CacheManagement` object
        Then all the cached keys are returned
            as `CacheKey` objects
        """
        # Given
        in_memory_cache_client = InMemoryCacheClient()
        in_memory_cache_client._cache = {
            "ukhsa:1:abc": mock.Mock(),
            "ukhsa:1:def456": mock.Mock(),
            "ukhsa:1:ns2-test-key": mock.Mock(),
        }
        cache_management = CacheManagement(
            in_memory=True,
            client=in_memory_cache_client,
        )

        # When
        all_cache_keys: list[str] = cache_management._get_all_cache_keys()

        # Then
        keys: list[str] = [cache_key._key for cache_key in all_cache_keys]

        assert "abc" in keys
        assert "def456" in keys
        assert "ns2-test-key" in keys

    def test_get_reserved_keys(self):
        """
        Given an `InMemoryCacheClient`
        When `get_reserved_keys()` is called
            from the `CacheManagement` object
        Then all the reserved namespace cache keys
            are returned as strings
        """
        # Given
        in_memory_cache_client = InMemoryCacheClient()
        in_memory_cache_client._cache = {
            "ukhsa:1:abc": mock.Mock(),
            "ukhsa:1:def456": mock.Mock(),
            "ukhsa:1:ns2-test-key": mock.Mock(),
        }
        cache_management = CacheManagement(
            in_memory=True,
            client=in_memory_cache_client,
        )

        # When
        reserved_keys: list[str] = cache_management.get_reserved_keys()

        # Then
        assert "ukhsa:1:abc" not in reserved_keys
        assert "ukhsa:1:def456" not in reserved_keys
        assert "ukhsa:1:ns2-test-key" in reserved_keys

    def test_get_non_reserved_keys(self):
        """
        Given an `InMemoryCacheClient`
        When `_get_non_reserved_keys()` is called
            from the `CacheManagement` object
        Then all the non-reserved namespace cache keys
            are returned as strings
        """
        # Given
        in_memory_cache_client = InMemoryCacheClient()
        in_memory_cache_client._cache = {
            "ukhsa:1:abc": mock.Mock(),
            "ukhsa:1:def456": mock.Mock(),
            "ukhsa:1:ns2-test-key": mock.Mock(),
        }
        cache_management = CacheManagement(
            in_memory=True,
            client=in_memory_cache_client,
        )

        # When
        non_reserved_keys: list[str] = cache_management._get_non_reserved_keys()

        # Then
        assert "ukhsa:1:abc" in non_reserved_keys
        assert "ukhsa:1:def456" in non_reserved_keys
        assert "ukhsa:1:ns2-test-key" not in non_reserved_keys

    def test_get_reserved_staging_keys(self):
        """
        Given an `InMemoryCacheClient`
        When `get_reserved_staging_keys()` is called
            from the `CacheManagement` object
        Then all the reserved staging namespace cache keys
            are returned as strings
        """
        # Given
        in_memory_cache_client = InMemoryCacheClient()
        reserved_staging_key = f"ukhsa:1:{RESERVED_NAMESPACE_STAGING_KEY_PREFIX}-789"
        in_memory_cache_client._cache = {
            "ukhsa:1:abc": mock.Mock(),
            "ukhsa:1:def456": mock.Mock(),
            f"ukhsa:1:{RESERVED_NAMESPACE_KEY_PREFIX}-test-key": mock.Mock(),
            reserved_staging_key: mock.Mock(),
        }
        cache_management = CacheManagement(
            in_memory=True,
            client=in_memory_cache_client,
        )

        # When
        reserved_staging_keys: list[CacheKey] = (
            cache_management.get_reserved_staging_keys()
        )

        # Then
        assert len(reserved_staging_keys) == 1
        assert reserved_staging_keys[0].is_reserved_staging_namespace
        assert reserved_staging_keys[0].full_key == reserved_staging_key

    def test_move_all_reserved_staging_keys_into_reserved_namespace_for_cache_client(
        self,
    ):
        """
        Given a number of keys in the non-reserved namespace
        And a key in the reserved staging namespace
        When `move_all_reserved_staging_keys_into_reserved_namespace()`
            is called from an instance of `CacheManagement`
        Then the `copy()` and `delete_many()` methods
            are called from the underlying client
            to move the key from the reserved staging namespace
            into the reserved namespace
        """
        # Given
        spy_cache_client = mock.Mock()
        reserved_staging_standalone_key = (
            f"{RESERVED_NAMESPACE_STAGING_KEY_PREFIX}-test-key"
        )
        reserved_staging_raw_key = f"ukhsa:1:{reserved_staging_standalone_key}"

        all_keys = [
            b"ukhsa:1:abc",
            b"ukhsa:1:def456",
            bytes(reserved_staging_raw_key, "utf-8"),
        ]
        spy_cache_client.list_keys.return_value = all_keys
        cache_management = CacheManagement(
            in_memory=False,
            client=spy_cache_client,
        )

        # When
        cache_management.move_all_reserved_staging_keys_into_reserved_namespace()

        # Then
        spy_cache_client.copy.assert_called_once_with(
            source=reserved_staging_raw_key,
            destination=f"ukhsa:1:{RESERVED_NAMESPACE_KEY_PREFIX}-test-key",
        )
        spy_cache_client.delete_many.assert_called_once_with(
            keys=[reserved_staging_raw_key]
        )
