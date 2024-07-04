import pytest

from cms.snippets.models.global_banner import BannerTypes, GlobalBanner
from cms.snippets.serializers.global_banner import get_active_global_banner
from tests.factories.cms.snippets.global_banner import GlobalBannerFactory


class TestGetActiveGlobalBanner:
    @pytest.mark.django_db
    def test_returns_data_for_active_banner(self):
        """
        Given a number of `GlobalBanner` records
            of which 1 has `is_active` set to True
        When `get_active_global_banner()` is called
        Then the correct `GlobalBanner` data is returned
        """
        # Given
        active_banner_info = {
            "title": "this is the active banner title",
            "body": "this is the active banner body",
            "banner_type": BannerTypes.WARNING.value,
            "is_active": True,
        }
        GlobalBannerFactory.create(**active_banner_info)
        inactive_banner_info = {
            "title": "this is the inactive banner title",
            "body": "this is the inactive banner body",
            "banner_type": BannerTypes.INFORMATION.value,
            "is_active": False,
        }
        GlobalBannerFactory.create(**inactive_banner_info)

        # When
        active_global_banner_info: dict[str, str] = get_active_global_banner(
            global_banner_manager=GlobalBanner.objects
        )

        # Then
        assert active_global_banner_info["title"] == active_banner_info["title"]
        assert active_global_banner_info["body"] == active_banner_info["body"]
        assert (
            active_global_banner_info["banner_type"]
            == active_banner_info["banner_type"]
        )
