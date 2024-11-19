import pytest

from metrics.api.enums import AppMode


class TestAppMode:
    @pytest.mark.parametrize(
        "expected_app_mode",
        [
            "CMS_ADMIN",
            "PRIVATE_API",
            "PUBLIC_API",
            "INGESTION",
            "FEEDBACK_API",
        ],
    )
    def test_dependent_on_db(self, expected_app_mode: str):
        """
        Given the `AppMode` Enum class
        When the `dependent_on_db()` method is called
        Then the correct values are returned
        """
        # Given / When
        app_modes_dependant_on_db = AppMode.dependent_on_db()

        # Then
        assert expected_app_mode in app_modes_dependant_on_db

    def test_dependent_on_cache(self):
        """
        Given the `AppMode` Enum class
        When the `dependent_on_cache()` method is called
        Then the correct values are returned
        """
        # Given / When
        app_modes_dependent_on_cache = AppMode.dependent_on_cache()

        # Then
        expected_values = {"PRIVATE_API"}
        assert set(app_modes_dependent_on_cache) == expected_values
