from caching.private_api.crawler import PrivateAPICrawler


class TestPrivateAPICrawlerCreate:
    # Tests for the create class methods

    def test_create_crawler_for_default_cache(self):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_default_cache`
            class method is called from the `PrivateAPICrawler` class
        Then the correct object is returned
        """
        # Given / When
        crawler = PrivateAPICrawler.create_crawler_for_default_cache()

        # Then
        assert not crawler._internal_api_client.reserved_namespace

    def test_create_crawler_to_force_write_in_reserved_staging_namespace(self):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_to_force_write_in_reserved_staging_namespace`
            class method is called from the `PrivateAPICrawler` class
        Then the correct object is returned
        """
        # Given / When
        crawler = (
            PrivateAPICrawler.create_crawler_to_force_write_in_reserved_staging_namespace()
        )

        # Then
        assert crawler._internal_api_client.reserved_namespace

    def test_create_crawler_for_lazy_loading(self):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_lazy_loading` class method
            is called from the `PrivateAPICrawler` class
        Then the correct object is returned
        """
        # Given / When
        crawler = PrivateAPICrawler.create_crawler_for_lazy_loading()

        # Then
        assert not crawler._internal_api_client.reserved_namespace
