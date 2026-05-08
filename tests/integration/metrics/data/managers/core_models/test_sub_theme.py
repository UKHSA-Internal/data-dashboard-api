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
