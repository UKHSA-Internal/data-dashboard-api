from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.hydrate_private_api_cache"


class TestHydratePrivateAPICommand:
    @mock.patch(f"{MODULE_PATH}.force_cache_refresh_for_all_pages")
    def test_delegates_call_successfully(
        self, spy_force_cache_refresh_for_all_pages: mock.MagicMock
    ):
        """
        Given an instance of the app
        When a call is made to the custom management command `hydrate_private_api_cache`
        Then the call is delegated to the `force_cache_refresh_for_all_pages()` function

        Patches:
            `spy_force_cache_refresh_for_all_pages`: For the main assertion
        """
        # Given / When
        call_command("hydrate_private_api_cache")

        # Then
        spy_force_cache_refresh_for_all_pages.assert_called_once()
