import hashlib
import json
from typing import Self

from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from caching.private_api.client import CacheClient, InMemoryCacheClient


class CacheMissError(Exception): ...


RESERVED_NAMESPACE_KEY_PREFIX = "ns2"


class CacheKey:
    def __init__(self, prefix: str, version: int, key: str):
        self._key = key
        self._prefix = prefix
        self._version = version

    def __repr__(self) -> str:
        return self.full_key

    def __str__(self) -> str:
        return self.standalone_key

    @classmethod
    def create(cls, raw_key: bytes | str) -> Self:
        raw_key = str(raw_key)
        raw_key = raw_key.strip("b'\"")
        prefix, version, key = raw_key.split(":")
        return cls(prefix=prefix, version=version, key=key)

    @property
    def full_key(self) -> str:
        return f"{self._prefix}:{self._version}:{self._key}"

    @property
    def standalone_key(self) -> str:
        return self._key

    @property
    def is_reserved_namespace(self) -> bool:
        return self._key.startswith(RESERVED_NAMESPACE_KEY_PREFIX)


class CacheManagement:
    """This is the abstraction used to save and retrieve items in the cache

    Notes:
        By passing `in_memory=True` to the constructor, an entirely in-memory cache
        can be used. Otherwise, the `django.core.cache` will be used.

    """

    def __init__(
        self,
        *,
        in_memory: bool,
        client: CacheClient | None = None,
        reserved_namespace_key_prefix: str = RESERVED_NAMESPACE_KEY_PREFIX,
    ):
        self._client = client or self._create_cache_client(in_memory=in_memory)
        self._reserved_namespace_key_prefix = reserved_namespace_key_prefix

    @staticmethod
    def _create_cache_client(*, in_memory: bool) -> CacheClient:
        """Creates a client used to interact with the cache component.

        Notes:
            An in-memory cache client is kept within the memory of this application.
            Since caching is achieved at the process level
            it is therefore ephemeral by nature.

            If `in_memory` is set to False a remote cache client will be created instead.

        Args:
            in_memory: Whether to use an entirely in-memory cache or not.

        Returns:
            An instantiated client object which exposes `get()` and `put()` methods

        """
        if in_memory:
            return InMemoryCacheClient()
        return CacheClient()

    def retrieve_item_from_cache(self, *, cache_entry_key: str) -> Response:
        """Retrieves the item from the cache matching the given `cache_entry_key`

        Args:
            cache_entry_key: The key of the item in the cache

        Returns:
            The item which was previously saved in the cache

        Raises:
            `CacheMissError`: If the item was not found in the cache

        """
        retrieved_entry = self._client.get(cache_entry_key=cache_entry_key)

        if retrieved_entry is None:
            raise CacheMissError

        return retrieved_entry

    def save_item_in_cache(
        self, *, cache_entry_key: str, item: Response, timeout: int | None
    ) -> Response:
        """Saves the item in the cache with the given `cache_entry_key`

        Notes:
            Depending on the client implementation,
            this will override the existing key if a clash is detected

        Args:
            cache_entry_key: The key of the item in the cache
            item: The item to be saved into the cache
            timeout: The number of seconds after which the response
                is expired and evicted from the cache

        Returns:
            The item which was just saved in the cache

        """
        item = self._render_response(response=item)
        self._client.put(cache_entry_key=cache_entry_key, value=item, timeout=timeout)
        return item

    def clear_non_reserved_keys(self):
        """Deletes all keys in the cache which are not within the reserved namespace

        Notes:
            This allows us to keep hold of
            expensive, infrequently changing data in the cache
            like maps data, whilst still allowing the
            cheaper more frequently changing data types like
            tables and charts to be cleared.

        Returns:
            None

        """
        non_reserved_keys: list[str] = self._get_non_reserved_keys()
        self._client.delete_many(keys=non_reserved_keys)

    def delete_many(self, keys: list[str]) -> None:
        """Deletes the given `keys` from the cache within 1 trip to the cache

        Returns:
            None

        """
        self._client.delete_many(keys=keys)

    def get_reserved_keys(self) -> list[str]:
        """Fetches all the keys in the reserved namespace of the cache

        Returns:
            List of reserved keys as strings.
            Note that only the key part is included in the string.
            This excludes the prefix and the version:
            full key representation = "ukhsa:1:ns2-abc123"
            returned key representation = "ns2-abc123"

        """
        all_cache_keys: list[CacheKey] = self._get_all_cache_keys()
        return [
            cache_key.standalone_key
            for cache_key in all_cache_keys
            if cache_key.is_reserved_namespace
        ]

    def _get_non_reserved_keys(self) -> list[str]:
        all_cache_keys: list[CacheKey] = self._get_all_cache_keys()
        return [
            cache_key.standalone_key
            for cache_key in all_cache_keys
            if not cache_key.is_reserved_namespace
        ]

    def _get_all_cache_keys(self) -> list[CacheKey]:
        all_raw_keys: list[bytes] = self._client.list_keys()
        return [CacheKey.create(raw_key=raw_key) for raw_key in all_raw_keys]

    def _render_response(self, *, response: Response) -> Response:
        if response.headers["Content-Type"] == "text/csv":
            return response

        return self._render_json_response(response=response)

    @staticmethod
    def _render_json_response(*, response: Response) -> Response:
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response

    # Cache key construction

    def build_cache_entry_key_for_request(
        self, *, request: Request, is_reserved_namespace: bool
    ) -> str:
        """Builds a hashed cache entry key for a request

        Args:
            request: The incoming request which is to be hashed
            is_reserved_namespace: Boolean switch to store the data
                in the reserved / long-lived namespace within the cache.
                Defaults to `False`.

        Returns:
            A hashed string representation
            of the given request taking its path
            and request body or query parameters into account
            depending on if it is a POST or GET request
            as well as whether the data sits
            in the reserved namespace or not.

        Raises:
            `ValueError`: If the request is not an HTTP GET or POST request

        """
        cache_key: str = self._build_standalone_key_for_request(request=request)
        if is_reserved_namespace:
            cache_key = f"{RESERVED_NAMESPACE_KEY_PREFIX}-{cache_key}"

        return cache_key

    def _build_standalone_key_for_request(self, *, request: Request) -> str:
        match request.method:
            case "POST":
                data = request.data
            case "GET":
                data = request.query_params.dict()
            case _:
                raise ValueError

        return self.build_cache_entry_key_for_data(
            endpoint_path=request.path, data=data
        )

    def build_cache_entry_key_for_data(
        self, *, endpoint_path: str, data: dict[str, str]
    ) -> str:
        """Builds a hashed cache entry key for the given `endpoint_path` and `data`

        Args:
            endpoint_path: The path of the endpoint being requested
            data: The data associated with the request

        Returns:
            A hashed string representation
            of the given `endpoint_path` and `data`

        """
        data = self._build_data_dict(endpoint_path=endpoint_path, data=data)
        return self.create_hash_for_data(data=data)

    @staticmethod
    def _build_data_dict(*, endpoint_path: str, data: dict[str, str]):
        endpoint_path: str = endpoint_path.strip("/")
        data = dict(sorted(data.items()))
        data["endpoint_path"] = endpoint_path
        return data

    @staticmethod
    def create_hash_for_data(*, data: dict) -> str:
        """Returns an SHA-256 hash of the given `data`

        Notes:
            The `data` is converted to a JSON string
            with sorted keys before calling out to the `hashlib` library

        Args:
            data: The provided data which is to be hashed

        Returns:
            A hashed string representation of the given `data`

        """
        sorted_serialized_data = json.dumps(
            obj=data, sort_keys=True, ensure_ascii=False
        )

        hashed_data = hashlib.sha256(sorted_serialized_data.encode())

        return hashed_data.hexdigest()
