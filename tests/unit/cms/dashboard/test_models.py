import pytest
from unittest import mock
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.test import override_settings

from cms.dashboard.models import UKHSAPage
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.composite_page_factory import FakeCompositePageFactory
from tests.fakes.factories.cms.landing_page_factory import FakeLandingPageFactory
from tests.fakes.factories.cms.metrics_documentation_factory import (
    FakeMetricsDocumentationParentPageFactory,
)
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.factories.cms.whats_new_child_entry_factory import (
    FakeWhatsNewChildEntryFactory,
)
from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)


class TestUKHSAPage:
    @pytest.mark.parametrize(
        "fake_page",
        [
            FakeTopicPageFactory.build_influenza_page_from_template(),
            FakeCommonPageFactory.build_blank_page(),
            FakeCompositePageFactory.build_page_from_template(
                page_name="access_our_data_getting_started"
            ),
            FakeLandingPageFactory.build_blank_page(),
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(),
            FakeWhatsNewChildEntryFactory.build_page_from_template(),
            FakeWhatsNewParentPageFactory.build_page_from_template(),
        ],
    )
    def test_is_previewable_is_inherited_from_ukhsa_page(self, fake_page: UKHSAPage):
        """
        Given a page model which inherits from UKHSAPage
        When checking the is_previewable implementation
        Then the method is inherited from UKHSAPage and matches current expected preview configuration
        Note: the expected previewability of each page type is currently False
        as we have implemented a custom preview view which does not rely on Wagtail's preview mechanism
        """
        # Given
        child_page = fake_page
        current_expected_previewability = {
            "FakeTopicPage": False,
            "FakeCommonPage": False,
            "FakeCompositePage": False,
            "FakeLandingPage": False,
            "FakeMetricsDocumentationParentPage": False,
            "FakeWhatsNewChildEntry": False,
            "FakeWhatsNewParentPage": False,
        }
        page_type = type(child_page).__name__

        # When
        page_is_previewable = child_page.is_previewable()

        # Then
        assert page_type in current_expected_previewability
        assert page_is_previewable is current_expected_previewability[page_type]
        assert type(child_page).is_previewable is UKHSAPage.is_previewable

    @pytest.mark.parametrize(
        "fake_page_with_expected_custom_preview",
        [
            {FakeTopicPageFactory.build_influenza_page_from_template: True},
            {FakeCommonPageFactory.build_blank_page: True},
            {
                lambda: FakeCompositePageFactory.build_page_from_template(
                    page_name="access_our_data_getting_started"
                ): True
            },
            {FakeLandingPageFactory.build_blank_page: True},
            {FakeMetricsDocumentationParentPageFactory.build_page_from_template: True},
            {FakeWhatsNewChildEntryFactory.build_page_from_template: True},
            {FakeWhatsNewParentPageFactory.build_page_from_template: True},
        ],
    )
    def test_custom_preview_enabled_matches_expected_page_type_value(
        self, fake_page_with_expected_custom_preview
    ):
        """
        Given a page model which inherits from UKHSAPage
        When checking the custom_preview_enabled attribute
        Then the inherited/customised value matches current expected per-page configuration
        Note: the expected value of custom_preview_enabled for each page type
        is based on whether the page type is currently configured to use the
        custom preview view.
        """
        # Given
        page_factory, expected_custom_preview_enabled = next(
            iter(fake_page_with_expected_custom_preview.items())
        )
        page = page_factory()

        # When
        custom_preview_enabled = bool(getattr(page, "custom_preview_enabled", False))

        # Then
        assert custom_preview_enabled is expected_custom_preview_enabled

    @pytest.mark.parametrize(
        "fake_page",
        [
            FakeTopicPageFactory.build_influenza_page_from_template(),
            FakeCommonPageFactory.build_blank_page(),
            FakeCompositePageFactory.build_page_from_template(
                page_name="access_our_data_getting_started"
            ),
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(),
            FakeWhatsNewChildEntryFactory.build_page_from_template(),
            FakeWhatsNewParentPageFactory.build_page_from_template(),
        ],
    )
    def test_show_in_menus_not_available_in_promote_panel(self, fake_page: UKHSAPage):
        """
        Given a blank page model which inherits from UKHSAPage
        When promote_panels is called
        Then show_in_menus is not available
        """
        # Given
        child_page = fake_page

        # When
        promote_panels = child_page.promote_panels

        # Then
        multi_field_panel = promote_panels[0]
        panel_names: list[str] = [p.clean_name for p in multi_field_panel.children]
        assert "show_in_menus" not in panel_names

    @pytest.mark.parametrize(
        "fake_page",
        [
            FakeCommonPageFactory.build_blank_page(),
            FakeCompositePageFactory.build_page_from_template(
                page_name="access_our_data_getting_started"
            ),
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(),
            FakeWhatsNewChildEntryFactory.build_page_from_template(),
            FakeWhatsNewParentPageFactory.build_page_from_template(),
        ],
    )
    @patch(
        "cms.dashboard.models.UKHSAPage.last_published_at",
        new_callable=mock.PropertyMock,
    )
    def test_last_updated_at_references_last_published_at(
        self, mock_last_published_at, fake_page: UKHSAPage
    ):
        """
        Given a blank page model which inherits from UKHSAPage which is not a TopicPage
        When the last_updated_at property is called
        Then the last_published_at field is referenced
        """
        # Given
        child_page = fake_page
        mock_last_published_at.return_value = "mocked_timestamp"

        # When
        timestamp = child_page.last_updated_at

        # Then
        assert timestamp == "mocked_timestamp"

    @pytest.mark.parametrize(
        "fake_page",
        [
            FakeTopicPageFactory.build_influenza_page_from_template(),
            FakeCommonPageFactory.build_blank_page(),
            FakeCompositePageFactory.build_page_from_template(
                page_name="access_our_data_getting_started"
            ),
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(),
            FakeWhatsNewChildEntryFactory.build_page_from_template(),
            FakeWhatsNewParentPageFactory.build_page_from_template(),
        ],
    )
    @patch.object(UKHSAPage, "_raise_error_if_slug_not_unique")
    def test_seo_title_field_is_required_by_clean_method_call(
        self,
        spy_raise_error_if_slug_not_unique: mock.MagicMock,
        fake_page: UKHSAPage,
    ):
        """
        Given a page model which inherits from UKHSAPage and no seo_title field was set
        When the clean() method is called
        Then a ValidationError is raised
        """
        # Given
        fake_page.seo_title = None

        # When / Then
        with pytest.raises(ValidationError):
            fake_page.clean()

    @patch("wagtail.models.Page.get_url", return_value=None)
    def test_get_url_returns_none_when_super_returns_none(
        self, spy_page_get_url: mock.MagicMock
    ):
        """Given no routable URL from Wagtail, return None unchanged."""
        page = FakeCommonPageFactory.build_blank_page()

        url = page.get_url()

        assert url is None

    @override_settings(FRONTEND_URL="")
    @patch("cms.dashboard.models.logger.error")
    @patch("wagtail.models.Page.get_url", return_value="/weather-health-alerts/")
    def test_get_url_returns_resolved_url_when_frontend_base_invalid(
        self,
        spy_page_get_url: mock.MagicMock,
        spy_logger_error: mock.MagicMock,
    ):
        """Given invalid frontend base URL, fallback to resolved URL."""
        page = FakeCommonPageFactory.build_blank_page()

        url = page.get_url()

        assert url == "/weather-health-alerts/"
        spy_logger_error.assert_called_once()

    @override_settings(FRONTEND_URL="http://localhost:3000")
    @patch("wagtail.models.Page.get_url", return_value="/weather-health-alerts/")
    def test_get_url_rewrites_relative_url_to_frontend_host(
        self,
        spy_page_get_url: mock.MagicMock,
    ):
        """Given a relative URL from Wagtail, rewrite to frontend host."""
        page = FakeCommonPageFactory.build_blank_page()

        url = page.get_url()

        assert url == "http://localhost:3000/weather-health-alerts/"

    @override_settings(FRONTEND_URL="http://localhost:3000")
    @patch(
        "wagtail.models.Page.get_url",
        return_value="http://localhost:8000/weather-health-alerts/",
    )
    def test_get_url_rewrites_absolute_url_to_frontend_host(
        self,
        spy_page_get_url: mock.MagicMock,
    ):
        """Given an absolute CMS URL from Wagtail, rewrite host to frontend."""
        page = FakeCommonPageFactory.build_blank_page()

        url = page.get_url()

        assert url == "http://localhost:3000/weather-health-alerts/"

    @patch("cms.dashboard.models.Page.objects")
    def test_raise_error_if_slug_not_unique_raises_validation_error(
        self,
        spy_page_objects: mock.MagicMock,
    ):
        """Given a duplicate live slug exists, raise ValidationError."""
        page = FakeCommonPageFactory.build_blank_page()
        page.slug = "weather-health-alerts"
        page.id = 17

        spy_page_objects.live.return_value.filter.return_value.exclude.return_value.exists.return_value = (
            True
        )

        with pytest.raises(ValidationError):
            page._raise_error_if_slug_not_unique()

    def test_get_url_parts_builds_expected_tuple(self):
        """Given site root path and page url_path, build expected URL parts tuple."""
        page = FakeCommonPageFactory.build_blank_page()
        page.url_path = "/root/weather-health-alerts/"

        site_root = mock.Mock(
            site_id=101, root_url="http://localhost:3000", root_path="/root/"
        )
        with patch.object(
            page, "_get_relevant_site_root_paths", return_value=(site_root,)
        ):
            result = page.get_url_parts(request=None)

        assert result == (101, "http://localhost:3000", "/weather-health-alerts/")

    def test_active_announcements_returns_values_list(self):
        """Given announcement queryset chain, active_announcements returns list of dicts."""
        page = mock.Mock()

        expected = [{"id": 1, "title": "t", "body": "b", "banner_type": 2}]
        values_qs = mock.Mock()
        values_qs.values.return_value = expected
        order_qs = mock.Mock()
        order_qs.order_by.return_value = values_qs
        filter_qs = mock.Mock()
        filter_qs.filter.return_value = order_qs

        page.announcements = filter_qs

        assert UKHSAPage.active_announcements.fget(page) == expected
