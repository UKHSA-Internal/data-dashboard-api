from unittest import mock

from caching.private_api.client import CacheClient, InMemoryCacheClient

MODULE_PATH = "caching.private_api.client"


class TestCacheClient:
    @mock.patch(f"{MODULE_PATH}.cache")
    def test_internal_cache_is_set_correctly(self, spy_cache: mock.MagicMock):
        """
        Given and instance of the `CacheClient`
        When the `_cache` attribute is called
        Then the `django.core.cache` is returned
        """
        # Given
        cache_client = CacheClient()

        # When
        internal_cache = cache_client._cache

        # Then
        assert internal_cache == spy_cache

    @mock.patch(f"{MODULE_PATH}.cache")
    def test_get_delegates_call(self, spy_cache: mock.MagicMock):
        """
        Given a cache entry key
        When `get()` is called from an instance of the `CacheClient`
        Then the call is delegated to the underlying cache
        """
        # Given
        fake_cache_entry_key = "abc"
        cache_client = CacheClient()

        # When
        returned_entry = cache_client.get(cache_entry_key=fake_cache_entry_key)

        # Then
        spy_cache.get.assert_called_once_with(key=fake_cache_entry_key, default=None)
        assert returned_entry == spy_cache.get.return_value

    @mock.patch(f"{MODULE_PATH}.cache")
    def test_put_delegates_call(self, spy_cache: mock.MagicMock):
        """
        Given a cache entry key
        When `put()` is called from an instance of the `CacheClient`
        Then the call is delegated to the underlying cache
        """
        # Given
        fake_cache_entry_key = "abc"
        mocked_value = mock.Mock()
        cache_client = CacheClient()

        # When
        cache_client.put(cache_entry_key=fake_cache_entry_key, value=mocked_value)

        # Then
        spy_cache.set.assert_called_once_with(
            key=fake_cache_entry_key, value=mocked_value, timeout=None
        )

    @mock.patch(f"{MODULE_PATH}.cache")
    def test_clear_delegates_call(self, spy_cache: mock.MagicMock):
        """
        Given an instance of the `CacheClient`
        When `clear()` is called from the client
        Then the call is delegated to the underlying cache
        """
        # Given
        cache_client = CacheClient()

        # When
        cache_client.clear()

        # Then
        spy_cache.clear.assert_called_once()

class TestInMemoryCacheClient:
    def test_put_stores_given_value(self):
        """
        Given a cache entry key and a value
        When `put()` is called from an instance of the `InMemoryCacheClient`
        Then the entry is added to the internal in memory cache
        """
        # Given
        mocked_value = mock.Mock()
        fake_cache_entry_key = "abc"
        in_memory_cache_client = InMemoryCacheClient()

        # When
        in_memory_cache_client.put(
            cache_entry_key=fake_cache_entry_key, value=mocked_value
        )

        # Then
        assert fake_cache_entry_key in in_memory_cache_client._cache

    def test_get_retrieves_given_value(self):
        """
        Given an entry which already exists in the cache
        When `get()` is called from an instance of the `InMemoryCacheClient`
        Then the value of the correct entry is returned
        """
        # Given
        mocked_value = mock.Mock()
        fake_cache_entry_key = "abc"
        in_memory_cache_client = InMemoryCacheClient()
        in_memory_cache_client._cache = {fake_cache_entry_key: mocked_value}

        # When
        retrieved_value = in_memory_cache_client.get(
            cache_entry_key=fake_cache_entry_key
        )

        # Then
        assert retrieved_value == mocked_value

    def test_get_returns_value_previously_added_via_put(self):
        """
        Given a cache entry key and a value
            which has been added via the `put()` method
        When `get()` is called from an instance of the `InMemoryCacheClient`
        Then the value of the correct entry is returned
        """
        # Given
        mocked_value = mock.Mock()
        fake_cache_entry_key = "abc"
        in_memory_cache_client = InMemoryCacheClient()

        in_memory_cache_client.put(
            cache_entry_key=fake_cache_entry_key, value=mocked_value
        )

        # When / Then
        retrieved_value = in_memory_cache_client.get(
            cache_entry_key=fake_cache_entry_key
        )

        # Then
        assert retrieved_value == mocked_value
