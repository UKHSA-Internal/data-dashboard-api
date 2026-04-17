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
