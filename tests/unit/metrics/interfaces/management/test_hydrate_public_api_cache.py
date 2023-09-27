from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.hydrate_public_api_cache"


class TestGenerateAPITimeSeries:
    @mock.patch(f"{MODULE_PATH}.crawl_public_api")
    def test_delegates_call_successfully(self, spy_crawl_public_api: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `hydrate_public_api_cache`
        Then the call is delegated to the `crawl_public_api()` function

        Patches:
            `spy_crawl_public_api`: For the main assertion
        """
        # Given / When
        call_command("hydrate_public_api_cache")

        # Then
        spy_crawl_public_api.assert_called_once()
