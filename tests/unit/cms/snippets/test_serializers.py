from cms.snippets.models.global_banner import BannerTypes, GlobalBanner
from cms.snippets.serializers import (
    ButtonSerializer,
    ExternalButtonSerializer,
    GlobalBannerResponseSerializer,
    GlobalBannerSerializer,
)
from tests.fakes.managers.cms.global_banner_manager import FakeGlobalBannerManager


class TestButtonSerializer:
    def test_can_serialize_payload(self):
        """
        Given a valid button model payload
        When this is serialized with a `ButtonSerializer`
        Then the correct validated data is returned
        """
        # Given
        text = "Download"
        loading_text = "Downloading"
        endpoint = "/api/bulkdownloads/v1"
        method = "POST"
        button_type = "DOWNLOAD"
        data = {
            "text": text,
            "loading_text": loading_text,
            "endpoint": endpoint,
            "method": method,
            "button_type": button_type,
        }

        # When
        serializer = ButtonSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["text"] == text
        assert serializer.validated_data["loading_text"] == loading_text
        assert serializer.validated_data["endpoint"] == endpoint
        assert serializer.validated_data["method"] == method
        assert serializer.validated_data["button_type"] == button_type


class TestExternalButtonSerializer:
    def test_can_serialize_payload(self):
        """
        Given a valid external_button model payload
        When this is serialized with a `ExternalButtonSerializer`
        Then the correct validated data is returned
        """
        text = "Download"
        url = "https://www.google.com"
        button_type = "Primary"
        icon = "Download"
        data = {
            "text": text,
            "url": url,
            "button_type": button_type,
            "icon": icon,
        }

        # When
        serializer = ExternalButtonSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Then
        assert serializer.validated_data["text"] == text
        assert serializer.validated_data["url"] == url
        assert serializer.validated_data["button_type"] == button_type
        assert serializer.validated_data["icon"] == icon


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
