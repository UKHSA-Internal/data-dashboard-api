from unittest import mock

import pytest

from cms.snippets.managers.global_banner import GlobalBannerManager
from cms.snippets.models.global_banner import (
    BannerTypes,
    GlobalBanner,
    MultipleGlobalBannersActiveError,
)


class TestGlobalBanner:
    @pytest.mark.parametrize(
        "expected_panel_name",
        [
            "title",
            "body",
            "banner_type",
            "is_active",
        ],
    )
    def test_panels(self, expected_panel_name: str):
        """
        Given a title, body and banner type
        When a `GlobalBanner` instance is created
        Then the correct panels are set
        """
        # Given
        title = "abc"
        body = "def"
        banner_type = BannerTypes.INFORMATION.value

        # When
        global_banner = GlobalBanner(
            title=title,
            body=body,
            banner_type=banner_type,
        )

        # Then
        panel_names: set[str] = {panel.field_name for panel in global_banner.panels}
        assert expected_panel_name in panel_names

    def test_enabled_set_false_by_default(self):
        """
        Given a `GlobalBanner` model
        When the object is initialized
        Then the `is_active` field is set to False by default
        """
        # Given
        title = "abc"
        body = "def"
        banner_type = BannerTypes.INFORMATION.value

        # When
        global_banner = GlobalBanner(
            title=title,
            body=body,
            banner_type=banner_type,
        )

        # Then
        assert global_banner.is_active is False

    def test_active_global_banner_produces_correct_dunder_str(self):
        """
        Given a `GlobalBanner`
            which has the `is_active` field set to True
        When the string representation is produced
        Then the string indicates it is the current global banner
        """
        # Given
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=True,
        )

        # When
        string_representation = str(global_banner)

        # Then
        current_active_banner_label = "Active information-level global banner"
        assert current_active_banner_label in string_representation
        assert "Inactive" not in string_representation

    def test_inactive_global_banner_produces_correct_dunder_str(self):
        """
        Given a `GlobalBanner`
            which has the `is_active` field set to False
        When the string representation is produced
        Then the string indicates it is an inactive global banner
        """
        # Given
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            banner_type=BannerTypes.INFORMATION.value,
            is_active=False,
        )

        # When
        string_representation = str(global_banner)

        # Then
        current_active_banner_label = "Active information-level global banner"
        assert current_active_banner_label not in string_representation
        assert "Inactive" in string_representation

    @mock.patch.object(GlobalBannerManager, "has_active_banner")
    def test_clean_raises_error_if_active_global_banner_already_exists(
        self, mocked_has_active_banner: mock.MagicMock
    ):
        """
        Given a `GlobalBanner`
            which is being set to active
        And the `GlobalBannerManager`
            which says there is already an active banner
        When the `clean()` method is called
            from the `GlobalBanner`
        Then the `MultipleGlobalBannersActiveError` is raised
        """
        # Given
        mocked_has_active_banner.return_value = True
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            is_active=True,
        )

        # When / Then
        with pytest.raises(MultipleGlobalBannersActiveError):
            global_banner.clean()

    @mock.patch.object(GlobalBannerManager, "has_active_banner")
    def test_clean_passes_when_current_banner_is_not_being_activated(
        self, mocked_has_active_banner: mock.MagicMock
    ):
        """
        Given a `GlobalBanner`
            which is not being set to active
        And the `GlobalBannerManager`
            which says there is already an active banner
        When the `clean()` method is called
            from the `GlobalBanner`
        Then no error is raised
        """
        # Given
        mocked_has_active_banner.return_value = True
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            is_active=False,
        )

        # When / Then
        global_banner.clean()

    @mock.patch.object(GlobalBannerManager, "has_active_banner")
    def test_clean_passes_when_current_banner_is_being_activated_as_only_active_banner(
        self, mocked_has_active_banner: mock.MagicMock
    ):
        """
        Given a `GlobalBanner` which is being set to active
        And the `GlobalBannerManager`
            which says there is not already an active banner
        When the `clean()` method is called
            from the `GlobalBanner`
        Then no error is raised
        """
        # Given
        mocked_has_active_banner.return_value = False
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            is_active=True,
        )

        # When / Then
        global_banner.clean()

    @mock.patch.object(GlobalBannerManager, "has_active_banner")
    def test_clean_passes_when_there_are_no_active_banners(
        self, mocked_has_active_banner: mock.MagicMock
    ):
        """
        Given a `GlobalBanner`
            which is not being set to active
        And the `GlobalBannerManager`
            which says there is not already an active banner
        When the `clean()` method is called
            from the `GlobalBanner`
        Then no error is raised
        """
        # Given
        mocked_has_active_banner.return_value = False
        global_banner = GlobalBanner(
            title="abc",
            body="def",
            is_active=False,
        )

        # When / Then
        global_banner.clean()
