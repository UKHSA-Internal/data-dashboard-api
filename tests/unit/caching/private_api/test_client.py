from unittest import mock

from caching.private_api.client import CacheClient, InMemoryCacheClient

MODULE_PATH = "caching.private_api.client"


class TestCacheClientForDefaultCache:
    @mock.patch(f"{MODULE_PATH}.caches")
    def test_get_delegates_call_for_default_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a cache entry key for the default cache
        When `get()` is called from an instance of the `CacheClient`
        Then the call is delegated
            to the underlying default cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()
        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__
        fake_cache_entry_key = "abc"
        cache_client = CacheClient()

        # When
        returned_entry = cache_client.get(cache_entry_key=fake_cache_entry_key)

        # Then
        spy_reserved_cache.get.assert_not_called()
        spy_default_cache.get.assert_called_once_with(
            key=fake_cache_entry_key, default=None
        )
        assert returned_entry == spy_default_cache.get.return_value

    @mock.patch(f"{MODULE_PATH}.caches")
    def test_put_delegates_call_for_default_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a cache entry key for default cache
        When `put()` is called from an instance of the `CacheClient`
        Then the call is delegated
            to the underlying default cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()
        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__

        fake_cache_entry_key = "abc"
        mocked_value = mock.Mock()
        cache_client = CacheClient(is_reserved_namespace=False)
        timeout = 123

        # When
        cache_client.put(
            cache_entry_key=fake_cache_entry_key, value=mocked_value, timeout=timeout
        )

        # Then
        spy_reserved_cache.set.assert_not_called()
        spy_default_cache.set.assert_called_once_with(
            key=fake_cache_entry_key, value=mocked_value, timeout=timeout
        )

    @mock.patch(f"{MODULE_PATH}.caches")
    def test_clear_for_default_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a `CacheClient` for the default cache
        When `clear()` is called from the client
        Then the call is delegated
            to the underlying default cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()

        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__

        cache_client = CacheClient(is_reserved_namespace=False)

        # When
        cache_client.clear()

        # Then
        spy_default_cache.clear.assert_called_once()
        spy_reserved_cache.clear.assert_not_called()


class TestCacheClientForReservedCache:
    @mock.patch(f"{MODULE_PATH}.caches")
    def test_get_delegates_call_for_reserved_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a cache entry key for the reserved cache
        When `get()` is called from an instance of the `CacheClient`
        Then the call is delegated
            to the underlying reserved cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()
        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__
        fake_cache_entry_key = "ns2-abc"
        cache_client = CacheClient(is_reserved_namespace=True)

        # When
        returned_entry = cache_client.get(cache_entry_key=fake_cache_entry_key)

        # Then
        spy_default_cache.get.assert_not_called()
        spy_reserved_cache.get.assert_called_once_with(
            key=fake_cache_entry_key, default=None
        )
        assert returned_entry == spy_reserved_cache.get.return_value

    @mock.patch(f"{MODULE_PATH}.caches")
    def test_put_delegates_call_for_reserved_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a cache entry key for reserved cache
        When `put()` is called from an instance of the `CacheClient`
        Then the call is delegated
            to the underlying reserved cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()
        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__

        fake_cache_entry_key = "ns2-abc"
        mocked_value = mock.Mock()
        cache_client = CacheClient(is_reserved_namespace=True)
        timeout = 123

        # When
        cache_client.put(
            cache_entry_key=fake_cache_entry_key, value=mocked_value, timeout=timeout
        )

        # Then
        spy_default_cache.set.assert_not_called()
        spy_reserved_cache.set.assert_called_once_with(
            key=fake_cache_entry_key, value=mocked_value, timeout=timeout
        )

<<<<<<< HEAD
    @mock.patch(f"{MODULE_PATH}.caches")
    def test_clear_for_reserved_cache(self, mocked_caches: mock.MagicMock):
        """
        Given a `CacheClient` for the reserved cache
        When `clear()` is called from the client
        Then the call is delegated
            to the underlying reserved cache
        """
        # Given
        spy_default_cache = mock.Mock()
        spy_reserved_cache = mock.Mock()

        caches = {"default": spy_default_cache, "reserved": spy_reserved_cache}
        mocked_caches.__getitem__.side_effect = caches.__getitem__

        cache_client = CacheClient(is_reserved_namespace=True)
=======
    @mock.patch(f"{MODULE_PATH}.cache")
    def test_clear(self, spy_cache: mock.MagicMock):
        """
        Given a `CacheClient`
        When `clear()` is called from the client
        Then the call is delegated
            to the underlying client
        """
        # Given
        cache_client = CacheClient()
>>>>>>> main

        # When
        cache_client.clear()

        # Then
<<<<<<< HEAD
        spy_default_cache.clear.assert_not_called()
        spy_reserved_cache.clear.assert_called_once()
=======
        spy_cache.clear.assert_called_once()
>>>>>>> main


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

    def test_clear_empties_the_cache(self):
        """
        Given a cache with an existing key
        When `clear()` is called from an instance of the `InMemoryCacheClient`
        Then the cache is emptied
        """
        # Given
        fake_cache = {"abc": mock.Mock()}
        in_memory_cache_client = InMemoryCacheClient()
        in_memory_cache_client._cache = fake_cache

        # When
        in_memory_cache_client.clear()

        # Then
        assert not in_memory_cache_client._cache
