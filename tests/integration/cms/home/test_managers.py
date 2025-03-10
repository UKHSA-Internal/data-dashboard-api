import pytest

from cms.home.managers import EXPECTED_LANDING_PAGE_SLUG
from cms.home.models import LandingPage


class TestLandingPageManager:
    @pytest.mark.django_db
    def test_get_landing_page(self):
        """
        Given 2 `LandingPage` records of which has a slug of "dashboard"
        When `get_landing_page()` is called from the `LandingPageManager`
        Then the correct `LandingPage` record is returned
        """
        # Given
        landing_page = LandingPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            sub_title="xyz",
            slug=EXPECTED_LANDING_PAGE_SLUG,
            seo_title="ABC",
        )
        invalid_landing_page = LandingPage.objects.create(
            path="def",
            depth=1,
            title="def",
            sub_title="uvw",
            slug="invalid_slug",
            seo_title="DEF",
        )

        # When
        retrieved_landing_page = LandingPage.objects.get_landing_page()

        # Then
        assert retrieved_landing_page == landing_page != invalid_landing_page
