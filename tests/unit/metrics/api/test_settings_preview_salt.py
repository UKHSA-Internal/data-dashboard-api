import importlib
import os
from unittest import mock

import pytest

import metrics.api.settings.default as default_settings

FRONTEND_URL_ENV_VAR = "FRONTEND_URL"


class TestPagePreviewTokenSalt:
    def test_build_page_previews_token_salt_is_stable_for_same_secret(self):
        """
        Given a fixed SECRET_KEY
        When page preview token salt is generated multiple times
        Then the generated salt is stable and has the expected length
        """
        # Given
        secret_key = "stable-secret-key"

        first_salt = default_settings._build_page_previews_token_salt.__globals__[
            "SECRET_KEY"
        ]
        default_settings._build_page_previews_token_salt.__globals__["SECRET_KEY"] = (
            secret_key
        )
        try:
            # When
            generated_salt = default_settings._build_page_previews_token_salt()
            regenerated_salt = default_settings._build_page_previews_token_salt()
        finally:
            default_settings._build_page_previews_token_salt.__globals__[
                "SECRET_KEY"
            ] = first_salt

        # Then
        assert generated_salt == regenerated_salt
        assert len(generated_salt) == 120

    def test_build_page_previews_token_salt_changes_with_secret(self):
        """
        Given two different SECRET_KEY values
        When page preview token salt is generated for each value
        Then each generated salt differs while preserving expected length
        """
        # Given
        original_secret = default_settings._build_page_previews_token_salt.__globals__[
            "SECRET_KEY"
        ]
        try:
            default_settings._build_page_previews_token_salt.__globals__[
                "SECRET_KEY"
            ] = "secret-one"

            # When
            first_salt = default_settings._build_page_previews_token_salt()

            default_settings._build_page_previews_token_salt.__globals__[
                "SECRET_KEY"
            ] = "secret-two"
            second_salt = default_settings._build_page_previews_token_salt()
        finally:
            default_settings._build_page_previews_token_salt.__globals__[
                "SECRET_KEY"
            ] = original_secret

        # Then
        assert first_salt != second_salt
        assert len(first_salt) == 120
        assert len(second_salt) == 120


class TestPagePreviewFrontendBaseUrlSetting:
    @mock.patch.dict(
        os.environ,
        {FRONTEND_URL_ENV_VAR: "https://preview-frontend.test"},
        clear=True,
    )
    def test_uses_env_var_value_for_frontend_base_url(self):
        """
        Given FRONTEND_URL is provided
        When settings are reloaded
        Then FRONTEND_URL is set from that env var

        Patches:
            `os.environ`: Provides the required frontend base URL during settings reload.
        """
        # Given
        provided_base_url = "https://preview-frontend.test"

        # When
        reloaded_settings = importlib.reload(default_settings)

        # Then
        assert reloaded_settings.FRONTEND_URL == provided_base_url

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_defaults_to_localhost_when_frontend_base_url_env_var_missing(self):
        """
        Given FRONTEND_URL is not provided
        When settings are reloaded
        Then FRONTEND_URL defaults to http://localhost:3000

        Patches:
            `os.environ`: Removes FRONTEND_URL before reloading settings.
        """
        reloaded_settings = importlib.reload(default_settings)

        assert reloaded_settings.FRONTEND_URL == "http://localhost:3000"
