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

    @pytest.mark.django_db
    def test_get_active_banners_orders_active_banners_by_priority_when_multiple_returned(
        self,
    ):
        """
        Given a number of `GlobalBanner` records
            of which multiple have `is_active` set to True
            and the `banner_type` is both `Warning` and `Information`
        When `get_active_banners()` is called
            from the `GlobalBannerManager`
        Then all active banners should be returned grouped by `banner_type`
            with `Warning` banners above `Information`.
        """
        # Given
        # Create multiple Information/Warning global banners.
        GlobalBannerFactory.create(is_active=True)
        GlobalBannerFactory.create(is_active=True, banner_type="Warning")
        GlobalBannerFactory.create(is_active=True)
        GlobalBannerFactory.create(is_active=True, banner_type="Warning")

        # When
        get_active_banners: GlobalBanner = GlobalBanner.objects.get_active_banners()

        # Then
        assert len(get_active_banners) == 4
        assert get_active_banners[0].banner_type == "Warning"
        assert get_active_banners[1].banner_type == "Warning"
        assert get_active_banners[2].banner_type == "Information"
        assert get_active_banners[3].banner_type == "Information"
