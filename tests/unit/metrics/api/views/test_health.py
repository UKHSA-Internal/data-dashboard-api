from unittest import mock

import pytest

from metrics.api.views import HealthView

MODULE_PATH = "metrics.api.views.health"


class TestHealthView:
    @pytest.mark.parametrize(
        "app_mode_environment_variable_value",
        [
            "PUBLIC_API",
            "CMS_ADMIN",
            "",
        ],
    )
    @mock.patch(f"{MODULE_PATH}.check_cache_for_all_pages")
    def test_does_not_check_for_cache_when_not_in_private_api_mode(
        self,
        spy_check_cache_for_all_pages: mock.MagicMock,
        app_mode_environment_variable_value: str,
    ):
        """
        Given the `APP_MODE` env var which is not `PRIVATE_API`
        When the `get()` method is called from the `HealthView`
        Then `check_cache_for_all_pages()` is not called
        """
        # Given
        with mock.patch("config.APP_MODE", app_mode_environment_variable_value):
            health_view = HealthView()

        # When
        health_view.get()

        # Then
        spy_check_cache_for_all_pages.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.check_cache_for_all_pages")
    def test_does_check_for_cache_in_private_api_mode(
        self,
        spy_check_cache_for_all_pages: mock.MagicMock,
    ):
        """
        Given the `APP_MODE` env var which is `PRIVATE_API`
        When the `get()` method is called from the `HealthView`
        Then `check_cache_for_all_pages()` is called
        """
        # Given
        with mock.patch("config.APP_MODE", "PRIVATE_API"):
            health_view = HealthView()

        # When
        health_view.get()

        # Then
        spy_check_cache_for_all_pages.assert_called_once()
