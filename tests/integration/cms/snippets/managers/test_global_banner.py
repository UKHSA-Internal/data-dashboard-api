import pytest
from django.utils import timezone
import datetime

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
            and the global banners are created with different times
        When `get_active_banners()` is called
            from the `GlobalBannerManager`
        Then all active banners should be returned grouped by `banner_type`
            with `Warning` banners above `Information` and with the most
            recently updated banners at the top of the banner_type group.
        """
        # Given
        # Create multiple Information/Warning global banners.
        info_banner_old = GlobalBannerFactory.create(is_active=True)
        warning_banner_old = GlobalBannerFactory.create(
            is_active=True, banner_type="Warning"
        )
        info_banner_new = GlobalBannerFactory.create(is_active=True)
        warning_banner_new = GlobalBannerFactory.create(
            is_active=True, banner_type="Warning"
        )

        # Update the updated on banners manually as this avoid the save method of the
        # model which will just set the updated_on value to the time that the test is ran
        now = timezone.now()
        GlobalBanner.objects.filter(id=info_banner_old.id).update(
            updated_on=now - datetime.timedelta(days=3)
        )
        GlobalBanner.objects.filter(id=warning_banner_old.id).update(
            updated_on=now - datetime.timedelta(days=2)
        )
        GlobalBanner.objects.filter(id=info_banner_new.id).update(
            updated_on=now - datetime.timedelta(days=1)
        )

        # When
        get_active_banners: GlobalBanner = GlobalBanner.objects.get_active_banners()

        # Then
        assert len(get_active_banners) == 4

        assert get_active_banners[0].banner_type == "Warning"
        assert get_active_banners[1].banner_type == "Warning"
        # assert that the first banner in the warning array was updated more recently than the second banner.
        assert get_active_banners[0].updated_on >= get_active_banners[1].updated_on

        assert get_active_banners[2].banner_type == "Information"
        assert get_active_banners[3].banner_type == "Information"
        assert get_active_banners[2].updated_on >= get_active_banners[3].updated_on
