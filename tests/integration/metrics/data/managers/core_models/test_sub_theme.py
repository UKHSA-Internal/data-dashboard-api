import pytest

from metrics.data.models.core_models.supporting import SubTheme
from tests.factories.metrics.sub_theme import SubThemeFactory


class TestSubThemeManager:
    @pytest.mark.django_db
    def test_query_for_unique_names(self):
        """
        Given a number of existing `SubTheme` records
        When `get_all_unique_names`is called
        Then a unique set of `SubTheme` records is returned
        """
        # Given
        fake_sub_theme_name_one = "respiratory"
        fake_sub_theme_name_two = "weather_alert"
        fake_sub_theme_name_three = "respiratory"

        SubThemeFactory(name=fake_sub_theme_name_one)
        SubThemeFactory(name=fake_sub_theme_name_two)
        SubThemeFactory(name=fake_sub_theme_name_three)

        # When
        all_sub_theme_names = SubTheme.objects.all()
        all_unique_sub_theme_names = SubTheme.objects.get_all_unique_names()

        # Then
        assert all_sub_theme_names.count() == 3
        assert all_unique_sub_theme_names.count() == 2

    @pytest.mark.django_db
    def test_query_for_get_all_names_and_ids(self):
        """
        Given a number of existing `SubTheme` records
        When `get_all_unique_names`is called
        Then a unique set of `SubTheme` records is returned
        """
        # Given
        fake_sub_theme_name_one = "respiratory"
        fake_sub_theme_name_two = "weather_alert"
        fake_sub_theme_name_three = "infectious_disease"

        SubThemeFactory(name=fake_sub_theme_name_one)
        SubThemeFactory(name=fake_sub_theme_name_two)
        SubThemeFactory(name=fake_sub_theme_name_three)

        # When
        all_sub_theme_names_and_ids = SubTheme.objects.get_all_names_and_ids()

        # Then
        assert all_sub_theme_names_and_ids.count() == 3

    @pytest.mark.django_db
    def test_query_for_get_name_by_id(self):
        """
        Given a number of existing `SubTheme` records
        When `get_name_by_id`is called
        Then a unique set of `SubTheme` records is returned
        """
        # Given
        fake_sub_theme_name_one = "respiratory"
        fake_sub_theme_name_two = "weather_alert"
        fake_sub_theme_name_three = "infectious_disease"

        SubThemeFactory(name=fake_sub_theme_name_one)
        SubThemeFactory(name=fake_sub_theme_name_two)
        SubThemeFactory(name=fake_sub_theme_name_three)

        # When
        get_name_by_id = SubTheme.objects.get_name_by_id(3)

        # Then
        assert get_name_by_id == fake_sub_theme_name_three

    @pytest.mark.django_db
    def test_get_filtered_unique_names_related_to_theme_returns_only_matching_records(
        self,
    ):
        """
        Given `SubTheme` records related to different parent themes
        When `get_filtered_unique_names_related_to_theme()` is called
        Then only the records for the given parent theme id are returned
        """
        # Given
        target_theme_id = 1
        other_theme_id = 2

        SubThemeFactory(name="respiratory", theme_id=target_theme_id)
        SubThemeFactory(name="immunisation", theme_id=target_theme_id)
        SubThemeFactory(name="weather_alert", theme_id=other_theme_id)

        # When
        filtered_sub_themes = (
            SubTheme.objects.get_filtered_unique_names_related_to_theme(
                parent_theme_id=target_theme_id
            )
        )

        # Then
        returned_names = {record["name"] for record in filtered_sub_themes}
        assert returned_names == {"respiratory", "immunisation"}
        assert filtered_sub_themes.count() == 2

    @pytest.mark.django_db
    def test_get_filtered_unique_names_related_to_theme_returns_empty_for_unrelated_theme(
        self,
    ):
        """
        Given `SubTheme` records related to a different parent theme
        When `get_filtered_unique_names_related_to_theme()` is called
            with a parent theme id that has no associated records
        Then an empty queryset is returned
        """
        # Given
        SubThemeFactory(name="respiratory", theme_id=1)

        # When
        filtered_sub_themes = (
            SubTheme.objects.get_filtered_unique_names_related_to_theme(
                parent_theme_id=999
            )
        )

        # Then
        assert filtered_sub_themes.count() == 0

    @pytest.mark.django_db
    def test_get_id_by_name_returns_id_for_existing_sub_theme(self):
        """
        Given an existing `SubTheme` record
        When `get_id_by_name()` is called
            from an instance of `SubThemeManager`
        Then the id of the matching record is returned
        """
        # Given
        sub_theme_name = "respiratory"
        sub_theme = SubThemeFactory(name=sub_theme_name)

        # When
        retrieved_id = SubTheme.objects.get_id_by_name(sub_theme_name)

        # Then
        assert retrieved_id == sub_theme.id

    @pytest.mark.django_db
    def test_get_id_by_name_returns_none_when_sub_theme_does_not_exist(self):
        """
        Given no matching `SubTheme` record
        When `get_id_by_name()` is called
            from an instance of `SubThemeManager`
        Then None is returned
        """
        # Given
        SubThemeFactory(name="respiratory")

        # When
        retrieved_id = SubTheme.objects.get_id_by_name("non_existent_sub_theme")

        # Then
        assert retrieved_id is None
