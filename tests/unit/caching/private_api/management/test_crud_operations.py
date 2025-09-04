from unittest import mock

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from caching.private_api.management import (
    CacheManagement,
    CacheMissError,
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
        )

        # When
        cache_management.clear()

        # Then
        spy_client.clear.assert_called_once()
