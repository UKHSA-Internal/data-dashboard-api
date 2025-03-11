import pytest

from cms.snippets.models import GlobalBanner
from tests.factories.cms.snippets.global_banner import GlobalBannerFactory


class TestGlobalBannerManager:
    @pytest.mark.django_db
    def test_get_active_banners(self):
        """
        Given a number of `GlobalBanner` records
            of which 1 has `is_active` set to True
        When `has_active_banner()` is called
            from the `GlobalBannerManager`
        Then True is returned
        """
        # Given
        GlobalBannerFactory.create(is_active=True)

        # When
        get_active_banners: GlobalBanner = GlobalBanner.objects.get_active_banners()

        # Then
        assert get_active_banners is not None
