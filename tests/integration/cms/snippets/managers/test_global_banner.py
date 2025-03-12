import pytest

from cms.snippets.models import GlobalBanner
from tests.factories.cms.snippets.global_banner import GlobalBannerFactory


class TestGlobalBannerManager:
    @pytest.mark.django_db
    def test_get_active_banners(self):
        """
        Given a number of `GlobalBanner` records
            of which 1 has `is_active` set to True
        When `get_active_banners()` is called
            from the `GlobalBannerManager`
        Then only one active banner should be returned
            and the active banner should be of type Information.
        """
        # Given
        GlobalBannerFactory.create(is_active=True)

        # When
        get_active_banners: GlobalBanner = GlobalBanner.objects.get_active_banners()

        # Then
        assert len(get_active_banners) == 1
        assert get_active_banners[0].banner_type == "Information"
