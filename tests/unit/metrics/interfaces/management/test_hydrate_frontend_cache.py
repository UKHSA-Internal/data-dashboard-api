from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.hydrate_frontend_cache"


class TestHydrateFrontendCache:
    @mock.patch(f"{MODULE_PATH}.crawl_front_end")
    def test_delegates_call_successfully(self, spy_crawl_front_end: mock.MagicMock):
        """
        Given an instance of the app
        When a call is made to the custom management command `hydrate_public_api_cache`
        Then the call is delegated to the `crawl_front_end()` function

        Patches:
            `spy_crawl_front_end`: For the main assertion
        """
        # Given / When
        call_command("hydrate_frontend_cache")

        # Then
        spy_crawl_front_end.assert_called_once()
