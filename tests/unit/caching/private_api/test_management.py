from http import HTTPMethod
from unittest import mock

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from caching.private_api.client import CacheClient, InMemoryCacheClient
from caching.private_api.management import CacheManagement, CacheMissError


@pytest.fixture
def cache_management_with_in_memory_cache() -> CacheManagement:
    return CacheManagement(in_memory=True)


class TestCacheManagement:
    # Tests for the __init__
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

    @pytest.mark.parametrize("in_memory", [True, False])
    @mock.patch.object(CacheManagement, "_create_cache_client")
    def test_create_cache_client_is_delegated_to_during_init_when_client_not_provided(
        self, spy_create_cache_client: mock.MagicMock, in_memory: bool
    ):
        """
        Given no pre-existing cache client
        When the `CacheManagement` class is initialized
        Then the call is delegated to the `_create_cache_client()` method
        """
        # Given / When
        cache_management = CacheManagement(in_memory=in_memory)

        # Then
        assert cache_management._client == spy_create_cache_client.return_value
        spy_create_cache_client.assert_called_once_with(in_memory=in_memory)

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

    # Tests for retrieving items via the cache client

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

    def test_create_hash_for_data(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given fake data
        When `create_hash_for_data()` is called
            from an instance of `CacheManagement`
        Then the correct SHA-256 hash string is returned
        """
        # Given
        fake_data = {"key_a": "value_a", "key_b": "value_b"}

        # When
        created_hash: str = cache_management_with_in_memory_cache.create_hash_for_data(
            data=fake_data
        )

        # Then
        assert (
            created_hash
            == "ddb57d211d9865a7c527caf1ee008c9c79f1c3ca361df9bf6081ce201922d5ec"
        )

    def test_create_hash_for_data_allows_for_correct_comparisons_for_keys_in_different_order(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given 2 dicts which are the same but have different orderings
        When `create_hash_for_data()` is called
            from an instance of `CacheManagement` for each dict
        Then the same SHA-256 hash string is returned
        """
        # Given
        fake_data = {"key_a": "value_a", "key_b": "value_b"}
        # Input dicts are the same except the key value pairs are in different order
        fake_data_to_be_compared = {"key_b": "value_b", "key_a": "value_a"}

        # When
        created_hash_one: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(data=fake_data)
        )
        created_hash_two: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(
                data=fake_data_to_be_compared
            )
        )

        # Then
        assert created_hash_one == created_hash_two

    def test_create_hash_for_data_allows_for_correct_comparisons_for_nested_data(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given 2 dicts which are the same but have different orderings
        When `create_hash_for_data()` is called
            from an instance of `CacheManagement` for each dict
        Then the same SHA-256 hash string is returned
        """
        # Given
        fake_data = {
            "key_a": "value_a",
            "key_b": ["value_b1", "value_b2"],
            "key_c": "value_c",
        }
        # Input dicts are the same except the key value pairs are in different order
        # And they also include a nested list
        fake_data_to_be_compared = {
            "key_a": "value_a",
            "key_c": "value_c",
            "key_b": ["value_b1", "value_b2"],
        }

        # When
        created_hash_one: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(data=fake_data)
        )
        created_hash_two: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(
                data=fake_data_to_be_compared
            )
        )

        # Then
        assert created_hash_one == created_hash_two

    def test_create_hash_for_data_allows_for_correct_comparisons_for_nested_dicts(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given 2 dicts which are the same but have different orderings
        When `create_hash_for_data()` is called
            from an instance of `CacheManagement` for each dict
        Then the same SHA-256 hash string is returned
        """
        # Given
        fake_data = {
            "key_a": "value_a",
            "key_b": [{"key_b1": "value_b2"}, {"key_b3": "value_b4"}],
            "key_c": "value_c",
        }
        # Input dicts are the same except the key value pairs are in different order
        # And they also include a nested list of dicts which should give the same hash
        fake_data_to_be_compared = {
            "key_a": "value_a",
            "key_c": "value_c",
            "key_b": [{"key_b1": "value_b2"}, {"key_b3": "value_b4"}],
        }

        # When
        created_hash_one: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(data=fake_data)
        )
        created_hash_two: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(
                data=fake_data_to_be_compared
            )
        )

        # Then
        assert created_hash_one == created_hash_two

    def test_create_hash_for_data_allows_for_correct_comparisons_for_nested_dicts_with_different_order_of_dicts(
        self, cache_management_with_in_memory_cache: CacheManagement
    ):
        """
        Given 2 dicts which are the same but have different orderings
        When `create_hash_for_data()` is called
            from an instance of `CacheManagement` for each dict
        Then the same SHA-256 hash string is returned
        """
        # Given
        fake_data = {
            "key_a": "value_a",
            "key_b": [{"key_b1": "value_b2"}, {"key_b3": "value_b4"}],
            "key_c": "value_c",
        }
        # Input dicts are the similar except the key value pairs are in different order at the top level
        # Here the dicts in the nested list of "key_b" should result in a different hash
        fake_data_to_be_compared = {
            "key_a": "value_a",
            "key_c": "value_c",
            "key_b": [{"key_b3": "value_b4"}, {"key_b1": "value_b2"}],
        }

        # When
        created_hash_one: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(data=fake_data)
        )
        created_hash_two: str = (
            cache_management_with_in_memory_cache.create_hash_for_data(
                data=fake_data_to_be_compared
            )
        )

        # Then
        assert created_hash_one != created_hash_two

    @pytest.mark.parametrize(
        "endpoint_path, data, expected_data",
        (
            [
                "api/charts/v3/",
                {"key_a": "value_a"},
                # expected dicts should bundle the endpoint path into the dicts
                {"key_a": "value_a", "endpoint_path": "api/charts/v3"},
            ],
            [
                "api/charts/v3",
                {"key_a": "value_a"},
                # expected dicts should treat endpoint paths with trailing `/` chars the same
                {"key_a": "value_a", "endpoint_path": "api/charts/v3"},
            ],
            [
                "api/charts/v3",
                {"key_b": "value_b", "key_a": "value_a"},
                # expected dict should sort key value pairs
                {
                    "key_a": "value_a",
                    "key_b": "value_b",
                    "endpoint_path": "api/charts/v3",
                },
            ],
        ),
    )
    @mock.patch.object(CacheManagement, "create_hash_for_data")
    def test_build_cache_entry_key_for_data(
        self,
        spy_create_hash_for_data: mock.MagicMock,
        endpoint_path: str,
        data: dict[str, str],
        expected_data: dict[str, str],
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given an endpoint path and input data
        When `build_cache_entry_key_for_data()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to the `create_hash_for_data()` method
        """
        # Given
        endpoint: str = endpoint_path
        input_data: dict = data

        # When
        created_hash = (
            cache_management_with_in_memory_cache.build_cache_entry_key_for_data(
                endpoint_path=endpoint,
                data=input_data,
            )
        )

        # Then
        spy_create_hash_for_data.assert_called_once_with(data=expected_data)
        assert created_hash == spy_create_hash_for_data.return_value

    @mock.patch.object(CacheManagement, "build_cache_entry_key_for_data")
    def test_build_cache_entry_key_for_request_post(
        self,
        spy_build_cache_entry_key_for_data: mock.MagicMock,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked POST request
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to `build_cache_entry_key_for_data()`
            with the correct args
        """
        # Given
        mocked_request = mock.Mock(method="POST")

        # When
        cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
            request=mocked_request
        )

        # Then
        spy_build_cache_entry_key_for_data.assert_called_once_with(
            endpoint_path=mocked_request.path, data=mocked_request.data
        )

    @mock.patch.object(CacheManagement, "build_cache_entry_key_for_data")
    def test_build_cache_entry_key_for_request_get(
        self,
        spy_build_cache_entry_key_for_data: mock.MagicMock,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked GET request
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then the call is delegated to `build_cache_entry_key_for_data()`
            with the correct args
        """
        # Given
        mocked_request = mock.MagicMock(method="GET")
        mocked_request.query_params.dict.return_value = {"param_a": "query_a"}

        # When
        cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
            request=mocked_request
        )

        # Then
        spy_build_cache_entry_key_for_data.assert_called_once_with(
            endpoint_path=mocked_request.path, data=mocked_request.query_params.dict()
        )

    @pytest.mark.parametrize(
        "invalid_http_method",
        (
            HTTPMethod.PUT,
            HTTPMethod.PATCH,
            HTTPMethod.DELETE,
            HTTPMethod.HEAD,
            HTTPMethod.CONNECT,
        ),
    )
    def test_build_cache_entry_key_for_request_raises_error_for_invalid_http_method(
        self,
        invalid_http_method: HTTPMethod,
        cache_management_with_in_memory_cache: CacheManagement,
    ):
        """
        Given a mocked request of an invalid HTTP method
        When `build_cache_entry_key_for_request()` is called
            from an instance of `CacheManagement`
        Then a `ValueError` is raised
        """
        # Given
        mocked_request = mock.MagicMock(method=invalid_http_method.value)

        # When / Then
        with pytest.raises(ValueError):
            cache_management_with_in_memory_cache.build_cache_entry_key_for_request(
                request=mocked_request
            )

    def test_clear(self):
        """
        Given an instance of `CacheManagement`
        When `clear()` is called from the object
        Then the call is delegated to the underlying client
        """
        # Given
        spy_client = mock.Mock()
        cache_management = CacheManagement(in_memory=True, client=spy_client)

        # When
        cache_management.clear()

        # Then
        spy_client.clear.assert_called_once()
