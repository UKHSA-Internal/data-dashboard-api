import pytest

from cms.snippets.models import GlobalBanner
from tests.factories.cms.snippets.global_banner import GlobalBannerFactory


class TestGlobalBannerManager:
    @pytest.mark.django_db
    def test_has_active_banner(self):
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
        has_active_banner: bool = GlobalBanner.objects.has_active_banner()

        # Then
        assert has_active_banner is True
