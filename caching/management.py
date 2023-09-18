import hashlib
import json
from typing import Optional

from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from caching.client import CacheClient, InMemoryCacheClient


class CacheMissError(Exception):
    ...


class CacheManagement:
    """This is the abstraction used to save and retrieve items in the cache

    Notes:
        By passing `in_memory=True` to the constructor, an entirely in-memory cache
        can be used. Otherwise, the `django.core.cache` will be used.

    """

    def __init__(self, in_memory: bool, client: Optional[CacheClient] = None):
        self._client = client or self._create_cache_client(in_memory=in_memory)

    @staticmethod
    def _create_cache_client(in_memory: bool) -> CacheClient:
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

    def retrieve_item_from_cache(self, cache_entry_key: str) -> Response:
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
            raise CacheMissError()

        return retrieved_entry

    def save_item_in_cache(self, cache_entry_key: str, item: Response) -> Response:
        """Saves the item in the cache with the given `cache_entry_key`

        Notes:
            Depending on the client implementation,
            this will override the existing key if a clash is detected

        Args:
            cache_entry_key: The key of the item in the cache
            item: The item to be saved into the cache

        Returns:
            The item which was just saved in the cache

        """
        item = self._render_response(response=item)
        self._client.put(cache_entry_key=cache_entry_key, value=item)
        return item

    def _render_response(self, response: Response) -> Response:
        if response.headers["Content-Type"] == "text/csv":
            return response

        return self._render_json_response(response=response)

    @staticmethod
    def _render_json_response(response: Response) -> Response:
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response

    def build_cache_entry_key_for_data(
        self, endpoint_path: str, data: dict[str, str]
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
    def _build_data_dict(endpoint_path: str, data: dict[str, str]):
        endpoint_path: str = endpoint_path.strip("/")
        data = dict(sorted(data.items()))
        data["endpoint_path"] = endpoint_path
        return data

    def build_cache_entry_key_for_request(self, request: Request) -> str:
        """Builds a hashed cache entry key for a request

        Args:
            request: The incoming request which is to be hashed

        Returns:
            A hashed string representation
            of the given request taking its path
            and request body or query parameters into account
            depending on if it is a POST or GET request.

        Raises:
            `ValueError`: If the request is not an HTTP GET or POST request

        """
        match request.method:
            case "POST":
                data = request.data
            case "GET":
                data = {
                    k: v
                    for k, v in request.query_params.dict().items()
                    if k.lower() != "body"
                }
            case _:
                raise ValueError()

        return self.build_cache_entry_key_for_data(
            endpoint_path=request.path, data=data
        )

    @staticmethod
    def create_hash_for_data(data: dict) -> str:
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
