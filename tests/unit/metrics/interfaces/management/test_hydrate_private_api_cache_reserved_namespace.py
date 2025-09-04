from unittest import mock

from django.core.management import call_command

MODULE_PATH = "metrics.interfaces.management.commands.hydrate_private_api_cache_reserved_namespace"


class TestHydratePrivateAPIReservedNamespaceCommand:
    @mock.patch(f"{MODULE_PATH}.refresh_reserved_cache")
    def test_delegates_call_successfully(
        self, spy_refresh_reserved_cache: mock.MagicMock
    ):
        """
        Given an instance of the app
        When a call is made to the custom management command `hydrate_private_api_cache`
        Then the call is delegated to the `refresh_reserved_cache()` function

        Patches:
            `spy_refresh_reserved_cache`: For the main assertion
        """
        # Given / When
        call_command("hydrate_private_api_cache_reserved_namespace")

        # Then
        spy_refresh_reserved_cache.assert_called_once()
