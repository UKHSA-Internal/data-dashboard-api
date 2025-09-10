import logging
from typing import Any

from django.core.cache import caches
from django.core.cache.backends.redis import RedisCache

logger = logging.getLogger(__name__)


RESERVED_NAMESPACE_KEY_PREFIX = "ns2"
RESERVED_CACHE_NAME = "reserved"
DEFAULT_CACHE_NAME = "default"


class CacheClient:
    _reserved_namespace_key_prefix = RESERVED_NAMESPACE_KEY_PREFIX
    """The client abstraction used to interact with the cache as set by the main Django application

    Notes:
        This should be used as the primary client for production.
        This provides an abstraction between our application and the caching implementation.

        The `is_reserved_namespace` arg dictates which cache to connect to.
        If True, this class will connect to the cache dedicated to long-lived / reserved data
        If False, the connection will be made to the cache designated for more ephemeral / normal data
        Defaults to False

    """

    def __init__(self, *, is_reserved_namespace: bool = False):
        self._preselect_cache(is_reserved_namespace=is_reserved_namespace)

    def _preselect_cache(self, *, is_reserved_namespace: bool):
        """Preselects the cache to connect to based on the given `is_reserved_namespace` boolean

        Notes:
            The preselected cache does not impact individual `get` and `put` operations.
            The preselected cache is provided to the `clear()` method only.
            So if you want to clear the default cache,
            Initialize this with is_reserved_namespace=False and call `clear()`
            If you wanted to clear the reserved cache, then you should
            initialize this with is_reserved_namespace=True and then call `clear()`

        """
        if is_reserved_namespace:
            self.pre_selected_cache_name = RESERVED_CACHE_NAME
        else:
            self.pre_selected_cache_name = DEFAULT_CACHE_NAME
        self.pre_selected_cache: RedisCache = caches[self.pre_selected_cache_name]

    def _select_cache_for_key(self, *, cache_entry_key: str) -> RedisCache:
        if cache_entry_key.startswith(f"{self._reserved_namespace_key_prefix}-"):
            return caches[RESERVED_CACHE_NAME]
        return caches[DEFAULT_CACHE_NAME]

    def get(self, *, cache_entry_key: str) -> Any | None:
        """Retrieves the cache entry associated with the given `cache_entry_key`

        Notes:
            This will fetch the entry from the relevant cache.
            i.e. if the given key begins with `ns2-`
            then the item will be fetched from the reserved cache.
            Otherwise, it will be fetched from the default cache

        Args:
            cache_entry_key: The string which acts as the
                identifier for the cache entry

        Returns:
            The value associated with the cache entry or None if not found

        """
        selected_cache: RedisCache = self._select_cache_for_key(
            cache_entry_key=cache_entry_key
        )
        return selected_cache.get(key=cache_entry_key, default=None)

    def put(self, *, cache_entry_key: str, value: Any, timeout: int | None) -> None:
        """Persists the entry within the cache

        Notes:
            This will place the entry within the relevant cache.
            i.e. if the given key begins with `ns2-`
            then the item will be placed in the reserved cache.
            Otherwise, it will be placed in the default cache

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
        selected_cache: RedisCache = self._select_cache_for_key(
            cache_entry_key=cache_entry_key
        )
        selected_cache.set(key=cache_entry_key, value=value, timeout=timeout)

    def clear(self):
        """Deletes all the keys in the cache - this is a wrapper around the FLUSHDB redis command

        Notes:
            Because we use Elasticache serverless v2 in
            production, which is a cluster. Listing all
            the keys and deleting them 1-by-1 doesn't work
            because AWS will only give you the keys on the
            shard the client is currently connected to.
            But the FLUSHDB command is distributed
            across every shard in the cluster.
            So this is the safer route to emptying the cache.

            The alternative would have been making application
            code cluster-aware i.e. iterating through each node
            and performing operations on each one.

        """
        is_cleared: bool = self.pre_selected_cache.clear()
        logger.info(
            "FLUSHDB command was executed in `%s` cache. Status: `%s`",
            self.pre_selected_cache_name,
            is_cleared,
        )


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
        super().__init__(
            is_reserved_namespace=False,
        )
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
        self._cache = {}
