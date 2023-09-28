from unittest import mock

from caching.internal_api_client import InternalAPIClient
from caching.private_api.crawler import PrivateAPICrawler


class TestCrawlerInit:
    # Tests for the __init__
    def test_internal_api_client_can_be_provided_to_init(self):
        """
        Given a pre-existing `InternalAPIClient`
        When the `Crawler` class is initialized
        Then the `_internal_api_client` is set with the provided client
        """
        # Given
        mocked_internal_api_client = mock.Mock()

        # When
        crawler = PrivateAPICrawler(internal_api_client=mocked_internal_api_client)

        # Then
        assert crawler._internal_api_client == mocked_internal_api_client

    @mock.patch.object(InternalAPIClient, "create_api_client")
    def test_internal_api_client_can_be_provided_to_init_(
        self, mocked_create_api_client: mock.MagicMock
    ):
        """
        Given no provided pre-existing `InternalAPIClient`
        When the `Crawler` class is initialized
        Then the `_internal_api_client` is set with an `InternalAPIClient` instance

        Patches:
            `mocked_create_api_client`: To isolate the side effect of
                creating an API key and therefore interacting with the db

        """
        # Given / When
        crawler = PrivateAPICrawler()

        # Then
        assert isinstance(crawler._internal_api_client, InternalAPIClient)
