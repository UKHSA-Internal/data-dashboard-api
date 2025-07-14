from typing import Any

from django.core.cache import cache


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

    def clear_non_ns2_keys(self) -> None:
        """Deletes all keys in the cache which do not contain the `ns2` keyword

        Notes:
            This allows us to keep hold of
            expensive, infrequently changing data in the cache
            like maps data, whilst still allowing the
            cheaper more frequently changing data types like
            tables and charts to be cleared.

        Returns:
            None

        """
        low_grade_keys = [key for key in self._cache.scan_iter() if "ns2" not in key]
        self._cache.delete_many(low_grade_keys)

    def clear(self) -> None:
        """Deletes all keys in the cache

        Returns:
            None

        """
        self._cache.clear()


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

    def clear(self) -> None:
        """Deletes all keys in the cache

        Returns:
            None

        """
        self._cache.clear()

    def clear_non_ns2_keys(self):
        """Deletes all keys in the cache which do not contain the `ns2` keyword

        Notes:
            This allows us to keep hold of
            expensive, infrequently changing data in the cache
            like maps data, whilst still allowing the
            cheaper more frequently changing data types like
            tables and charts to be cleared.

        Returns:
            None

        """
        for key in self._cache.keys():
            if "ns2" not in key:
                self._cache.pop(key)
