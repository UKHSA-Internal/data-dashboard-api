from unittest import mock

from caching.internal_api_client import InternalAPIClient
from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.dynamic_block_crawler import DynamicContentBlockCrawler
from caching.private_api.crawler.geographies_crawler import GeographiesAPICrawler
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser


class TestPrivateAPICrawlerInit:
    # Tests for the __init__
    def test_internal_api_client_can_be_provided_to_init(self):
        """
        Given a pre-existing `InternalAPIClient`
        When the `PrivateAPICrawler` class is initialized
        Then the `_internal_api_client` is set with the provided client
        """
        # Given
        mocked_internal_api_client = mock.Mock()

        # When
        crawler = PrivateAPICrawler(internal_api_client=mocked_internal_api_client)

        # Then
        assert crawler._internal_api_client == mocked_internal_api_client

    def test_internal_api_client_is_created_when_not_provided_to_init(self):
        """
        Given no provided pre-existing `InternalAPIClient`
        When the `PrivateAPICrawler` class is initialized
        Then the `_internal_api_client` is set with an `InternalAPIClient` instance

        Patches:
            `mocked_create_api_client`: To isolate the side effect of
                creating an API key and therefore interacting with the db

        """
        # Given / When
        crawler = PrivateAPICrawler()

        # Then
        assert isinstance(crawler._internal_api_client, InternalAPIClient)

    def test_cms_block_parser_is_created_when_not_provided_to_init(self):
        """
        Given no provided pre-existing `CMSBlockParser`
        When the `PrivateAPICrawler` class is initialized
        Then the `_cms_block_parser` is set with an `CMSBlockParser` instance
        """
        # Given / When
        crawler = PrivateAPICrawler()

        # Then
        assert isinstance(crawler._cms_block_parser, CMSBlockParser)

    def test_dynamic_content_block_crawler_is_created_when_not_provided_to_init(self):
        """
        Given no provided pre-existing `DynamicContentBlockCrawler`
        When the `PrivateAPICrawler` class is initialized
        Then the `_dynamic_content_block_crawler` is set
            with an `DynamicContentBlockCrawler` instance
        """
        # Given / When
        crawler = PrivateAPICrawler()

        # Then
        assert isinstance(
            crawler._dynamic_content_block_crawler, DynamicContentBlockCrawler
        )

    def test_geographies_api_is_initialized(self):
        """
        Given an `InternalAPIClient`
        When the `PrivateAPICrawler` class is initialized
        Then the `_internal_api_client` is set
            on the `GeographiesAPICrawler` class is initialized
        """
        # Given
        mocked_internal_api_client = mock.Mock()

        # When
        crawler = PrivateAPICrawler(internal_api_client=mocked_internal_api_client)

        # Then
        geographies_api_crawler = crawler.geography_api_crawler
        assert isinstance(geographies_api_crawler, GeographiesAPICrawler)
        assert (
            geographies_api_crawler._internal_api_client == mocked_internal_api_client
        )
