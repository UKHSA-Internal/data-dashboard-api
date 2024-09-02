import pytest

from cms.home.managers import EXPECTED_HOME_PAGE_SLUG
from cms.home.models import HomePage


class TestHomePageManager:
    @pytest.mark.django_db
    def test_get_landing_page(self):
        """
        Given 2 `HomePage` records of which only 1 has a slug of "dashboard"
        When `get_landing_page()` is called from the `HomePageManager`
        Then the correct `HomePage` record is returned
        """
        # Given
        landing_page = HomePage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            slug=EXPECTED_HOME_PAGE_SLUG,
            seo_title="ABC",
        )
        invalid_page = HomePage.objects.create(
            path="def",
            depth=1,
            title="def",
            slug="invalid_slug",
            seo_title="DEF",
        )

        # When
        retrieved_landing_page = HomePage.objects.get_landing_page()

        # Then
        assert retrieved_landing_page == landing_page != invalid_page
