from typing import Any

from django.core.cache import cache

from metrics.api import settings


class CacheClient:
    """The client abstraction used to interact with the cache as set by the main Django application

    Notes:
        This should be used as the primary client for production.
        This provides an abstraction between our application and the caching implementation.

    """

    def __init__(self):
        self._cache = cache

    def get(self, *, cache_entry_key: str) -> Any | None:
        """Retrieves the cache entry associated with the given `cache_entry_key`

        Args:
            cache_entry_key: The string which acts as the
                identifier for the cache entry

        Returns:
            The value associated with the cache entry or None if not found

        """
        return self._cache.get(key=cache_entry_key, default=None)

    def put(self, *, cache_entry_key: str, value: Any, timeout: int | None) -> None:
        """Persists the entry within the cache

        Args:
            cache_entry_key: The string which acts as the
                identifier for the cache entry
            value: The content being stored in the cache
                for this entry
            timeout: The number of seconds after which the response
                is expired and evicted from the cache

        Returns:
            None

        """
        self._cache.set(key=cache_entry_key, value=value, timeout=timeout)

    def list_keys(self) -> list[bytes]:
        """Lists all the application-level keys in the cache

        Notes:
            This is the Django cache <-> Redis implementation
            for listing all the keys in the cache.

        Returns:
            List of bytes where each byte represents a single key

        """
        key_prefix: str = settings.CACHES["default"]["KEY_PREFIX"]
        low_level_client = self._cache._cache.get_client()
        pattern = f"*{key_prefix}*"
        return low_level_client.keys(pattern)

    def delete_many(self, keys: list[str]) -> None:
        """Deletes all the provided keys in the cache

        Args:
            keys: The cache keys to delete
                within a bulk delete operation

        Returns:
            None

        """
        self._cache.delete_many(keys=keys)


class InMemoryCacheClient(CacheClient):
    """The client abstraction used to interact with an in-memory version the cache.

    Notes:
        This can be used as an alternative to the concrete `CacheClient`
        for testing purposes.
        This can also be used in place of the main cache altogether
        for local development.
        This is to provide engineers the option of running the application
        without additional infrastructure i.e. `Redis`

    """

    def __init__(self):
        super().__init__()
        self._cache = {}

    def get(self, *, cache_entry_key: str) -> Any:
        """Retrieves the cache entry associated with the given `cache_entry_key`

        Args:
            cache_entry_key: The string which acts as the
                identifier for the cache entry

        Returns:
            The value associated with the cache entry or None if not found

        """
        return self._cache.get(cache_entry_key, None)

    def put(self, *, cache_entry_key: str, value: Any, **kwargs) -> None:
        """Persists the entry within the cache

        Args:
            cache_entry_key: The string which acts as the
                identifier for the cache entry
            value: The content being stored in the cache
                for this entry

        Returns:
            None

        """
        self._cache[cache_entry_key] = value

    def delete_many(self, *, keys: list) -> None:
        """Deletes all keys in the cache which are not within the reserved namespace

        Args:
            keys: The cache keys to delete
                within a bulk delete operation

        Returns:
            None

        """
        for key in keys:
            self._cache.pop(key)

    def list_keys(self) -> list[bytes]:
        """Lists all the keys in the cache as bytes"""
        return [bytes(key, encoding="utf-8") for key in self._cache]
