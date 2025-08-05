from http import HTTPMethod
from unittest import mock

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from caching.private_api.client import CacheClient, InMemoryCacheClient
from caching.private_api.management import (
    CacheManagement,
    CacheMissError,
    RESERVED_NAMESPACE_KEY_PREFIX,
)


class TestCacheManagementCreateHashForData:
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
