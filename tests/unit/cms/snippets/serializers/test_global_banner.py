from cms.snippets.models.global_banner import BannerTypes, GlobalBanner
from cms.snippets.serializers import (
    GlobalBannerResponseSerializer,
    GlobalBannerSerializer,
)
from tests.fakes.managers.cms.global_banner_manager import FakeGlobalBannerManager


class TestGlobalBannerResponseSerializer:
    def test_serializes_model_correctly(self):
        """
        Given a `GlobalBanner` model instance
        When the model is passed to a `GlobalBannerResponseSerializer`
        Then the output `data` contains the correct fields
        """
        # Given
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            banner_type=BannerTypes.INFORMATION.value,
        )

        # When
        serializer = GlobalBannerResponseSerializer(instance=global_banner)

        # Then
        expected_data = {
            "title": global_banner.title,
            "body": global_banner.body,
            "banner_type": global_banner.banner_type,
        }
        assert serializer.data == expected_data

    def test_data_returns_none_if_no_model_instance_is_provided(self):
        """
        Given no `GlobalBanner` model instance is provided
        When this is passed to a `GlobalBannerResponseSerializer`
        Then the output `data` returns None
        """
        # Given / When
        serializer = GlobalBannerResponseSerializer(instance=None)

        # Then
        assert serializer.data is None


class TestGlobalBannerSerializer:
    def test_serialized_data_for_active_global_banner(self):
        """
        Given a `GlobalBanner` model instance which is active
        And an inactive `GlobalBanner` model instance
        When `data` is called from an instance
            of the `GlobalBannerSerializer`
        Then the output `data` contains info
            about the currently active global banner
        """
        # Given
        active_global_banner = GlobalBanner(
            title="abc",
            body="def",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=True,
        )
        inactive_global_banner = GlobalBanner(
            title="123",
            body="456",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=False,
        )
        fake_global_banner_manager = FakeGlobalBannerManager(
            global_banners=[active_global_banner, inactive_global_banner]
        )

        # When
        serializer = GlobalBannerSerializer(
            context={"global_banner_manager": fake_global_banner_manager}
        )

        # Then
        expected_data = {
            "active_global_banner": {
                "title": active_global_banner.title,
                "body": active_global_banner.body,
                "banner_type": active_global_banner.banner_type,
            }
        }
        assert serializer.data == expected_data

    def test_serialized_data_for_no_active_global_banner(self):
        """
        Given a number of `GlobalBanner` model instances
            of which none are active
        When `data` is called from an instance
            of the `GlobalBannerSerializer`
        Then the output `data` states
            the active global banner as None

        """
        # Given
        first_inactive_global_banner = GlobalBanner(
            title="abc",
            body="def",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=False,
        )
        second_inactive_global_banner = GlobalBanner(
            title="123",
            body="456",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=False,
        )
        fake_global_banner_manager = FakeGlobalBannerManager(
            global_banners=[first_inactive_global_banner, second_inactive_global_banner]
        )

        # When
        serializer = GlobalBannerSerializer(
            context={"global_banner_manager": fake_global_banner_manager}
        )

        # Then
        expected_data = {"active_global_banner": None}
        assert serializer.data == expected_data
