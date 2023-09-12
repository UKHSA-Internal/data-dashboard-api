from unittest import mock

from caching.crawler import Crawler
from caching.internal_api_client import InternalAPIClient


class TestCrawlerCreate:
    # Tests for the create class methods

    @mock.patch.object(InternalAPIClient, "create_api_client")
    def test_create_crawler_for_cache_checking_only(
        self, mocked_create_api_client: mock.MagicMock
    ):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_cache_checking_only` class method
            is called from the `Crawler` class
        Then the correct object is returned

        Patches:
            `mocked_create_api_client`: To remove the side effect
                of having to create an API key and therefore hit the db
        """
        # Given / When
        crawler = Crawler.create_crawler_for_cache_checking_only()

        # Then
        assert crawler._internal_api_client.cache_check_only

    @mock.patch.object(InternalAPIClient, "create_api_client")
    def test_create_crawler_for_force_cache_refresh(
        self, mocked_create_api_client: mock.MagicMock
    ):
        """
        Given no pre-existing `InternalAPIClient`
        When the `create_crawler_for_force_cache_refresh` class method
            is called from the `Crawler` class
        Then the correct object is returned

        Patches:
            `mocked_create_api_client`: To remove the side effect
                of having to create an API key and therefore hit the db
        """
        # Given / When
        crawler = Crawler.create_crawler_for_force_cache_refresh()

        # Then
        assert crawler._internal_api_client.force_refresh
