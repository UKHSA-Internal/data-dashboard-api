from caching.private_api.crawler import PrivateAPICrawler


class TestCrawlerCreate:
    # Tests for the create class methods

    def test_create_crawler_for_cache_checking_only(self):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_cache_checking_only` class method
            is called from the `Crawler` class
        Then the correct object is returned
        """
        # Given / When
        crawler = PrivateAPICrawler.create_crawler_for_cache_checking_only()

        # Then
        assert crawler._internal_api_client.cache_check_only

    def test_create_crawler_for_force_cache_refresh(self):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_force_cache_refresh` class method
            is called from the `Crawler` class
        Then the correct object is returned
        """
        # Given / When
        crawler = PrivateAPICrawler.create_crawler_for_force_cache_refresh()

        # Then
        assert crawler._internal_api_client.force_refresh
