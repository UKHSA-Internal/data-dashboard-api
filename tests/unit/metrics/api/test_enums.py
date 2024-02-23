from metrics.api.enums import AppMode


class TestAppMode:
    def test_dependent_on_db(self):
        """
        Given the `AppMode` Enum class
        When the `dependent_on_db()` method is called
        Then the correct values are returned
        """
        # Given / When
        app_modes_dependant_on_db = AppMode.dependent_on_db()

        # Then
        expected_values = {"CMS_ADMIN", "PRIVATE_API", "PUBLIC_API", "INGESTION"}
        assert set(app_modes_dependant_on_db) == expected_values

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
