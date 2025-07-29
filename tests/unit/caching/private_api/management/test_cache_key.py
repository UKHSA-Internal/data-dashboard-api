from caching.private_api.management import CacheKey, RESERVED_NAMESPACE_KEY_PREFIX


class TestCacheKey:
    def test_create(self):
        """
        Given a raw cache key in bytes format
        When the `create()` method is called
            from the `CacheKey` class
        Then the returned object holds
            reference to the deconstructed key parts
        """
        # Given
        key = "abc123"
        prefix = "ukhsa"
        version = "1"
        raw_key = f"{prefix}:{version}:{key}"
        raw_key = bytes(raw_key, encoding="utf-8")

        # When
        cache_key = CacheKey.create(raw_key=raw_key)

        # Then
        assert cache_key._key == key
        assert cache_key._prefix == prefix
        assert cache_key._version == version

    def test_standalone_key(self):
        """
        Given a `CacheKey` object
        When the `standalone_key` property is called
        Then the standalone key part is returned as a string
        """
        # Given
        key = "abc123"
        prefix = "ukhsa"
        version = "1"
        raw_key = f"{prefix}:{version}:{key}"
        raw_key = bytes(raw_key, encoding="utf-8")
        cache_key = CacheKey.create(raw_key=raw_key)

        # When
        standalone_key: str = cache_key.standalone_key

        # Then
        assert standalone_key == key

    def test_full_key(self):
        """
        Given a `CacheKey` object
        When the `full_key` property is called
        Then the entirety of the key is returned as a string
        """
        # Given
        key = "abc123"
        prefix = "ukhsa"
        version = "1"
        raw_key = f"{prefix}:{version}:{key}"
        raw_key = bytes(raw_key, encoding="utf-8")
        cache_key = CacheKey.create(raw_key=raw_key)

        # When
        full_key: str = cache_key.full_key

        # Then
        assert full_key == raw_key.decode("utf-8")

    def test_is_reserved_namespace_returns_true_for_reserved_key(self):
        """
        Given a raw cache key in bytes format
            which is set within the reserved namespace
        When the `is_reserved_namespace()` property is called
            from the `CacheKey` class
        Then True is returned
        """
        # Given
        key = "abc123"
        prefix = "ukhsa"
        version = "1"
        raw_key = f"{prefix}:{version}:{RESERVED_NAMESPACE_KEY_PREFIX}-{key}"
        raw_key = bytes(raw_key, "utf-8")

        # When
        cache_key = CacheKey.create(raw_key=raw_key)

        # Then
        assert cache_key.is_reserved_namespace

    def test_is_reserved_namespace_returns_false_for_non_reserved_key(self):
        """
        Given a raw cache key in bytes format
            which is not set within the reserved namespace
        When the `is_reserved_namespace()` property is called
            from the `CacheKey` class
        Then False is returned
        """
        # Given
        key = "abc123"
        prefix = "ukhsa"
        version = "1"
        raw_key = f"{prefix}:{version}:{key}"
        raw_key = bytes(raw_key, "utf-8")

        # When
        cache_key = CacheKey.create(raw_key=raw_key)

        # Then
        assert not cache_key.is_reserved_namespace
