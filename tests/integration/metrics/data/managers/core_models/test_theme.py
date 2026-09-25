import pytest

from metrics.data.models.core_models.supporting import Theme
from tests.factories.metrics.theme import ThemeFactory


class TestThemeManager:
    @pytest.mark.django_db
    def test_query_get_all_names_and_ids(self):
        """
        Given a number of existing `Topic` records
        When `get_all_names_and_ids` is called
        Then a unique set of `Topic` records is returned.
        """
        # Given
        fake_theme_name_one = "respiratory"
        fake_theme_name_two = "infectious_disease"
        fake_theme_name_three = "immunisation"

        ThemeFactory(name=fake_theme_name_one)
        ThemeFactory(name=fake_theme_name_two)
        ThemeFactory(name=fake_theme_name_three)

        # When
        get_all_names_and_ids = Theme.objects.get_all_names_and_ids()

        # Then
        assert get_all_names_and_ids.count() == 3

    @pytest.mark.django_db
    def test_query_get_name_by_id(self):
        """
        Given a number of existing `Topic` records
        When `get_all_names_and_ids` is called
        Then a unique set of `Topic` records is returned.
        """
        # Given
        fake_theme_name_one = "respiratory"
        fake_theme_name_two = "infectious_disease"
        fake_theme_name_three = "immunisation"

        ThemeFactory(name=fake_theme_name_one)
        ThemeFactory(name=fake_theme_name_two)
        ThemeFactory(name=fake_theme_name_three)

        # When
        get_name_by_id = Theme.objects.get_name_by_id(2)

        # Then
        assert get_name_by_id == fake_theme_name_two

    @pytest.mark.django_db
    def test_get_id_by_name_returns_id_for_existing_theme(self):
        """
        Given an existing `Theme` record
        When `get_id_by_name()` is called
            from an instance of `ThemeManager`
        Then the id of the matching record is returned
        """
        # Given
        theme_name = "respiratory"
        theme = ThemeFactory(name=theme_name)

        # When
        retrieved_id = Theme.objects.get_id_by_name(theme_name)

        # Then
        assert retrieved_id == theme.id

    @pytest.mark.django_db
    def test_get_id_by_name_returns_none_when_theme_does_not_exist(self):
        """
        Given no matching `Theme` record
        When `get_id_by_name()` is called
            from an instance of `ThemeManager`
        Then None is returned
        """
        # Given
        ThemeFactory(name="respiratory")

        # When
        retrieved_id = Theme.objects.get_id_by_name("non_existent_theme")

        # Then
        assert retrieved_id is None
