from unittest import mock

import pytest
from django.core.exceptions import ValidationError

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
        Given a page model which inherits from `UKHSAPage`
        When checking the `is_previewable` implementation
        Then the method is inherited from `UKHSAPage` and matches current expected preview configuration
           Note: the expected previewability of each page type is currently `False`
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
            {FakeCommonPageFactory.build_blank_page: False},
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
        Given a page model which inherits from `UKHSAPage`
        When checking the `custom_preview_enabled` attribute
        Then the inherited/customised value matches current expected per-page configuration
            Note: the expected value of `custom_preview_enabled` for each page type
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
        Given a blank page model which inherits from `UKHSAPage`
        When `promote_panels` is called
        Then `show_in_menus` is not available
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
    def test_last_updated_at_references_last_published_at(self, fake_page: UKHSAPage):
        """
        Given a blank page model which inherits from `UKHSAPage`
            which is **not** a `TopicPage`
        When the `last_updated_at` property is called
        Then the `last_published_at` field is referenced
        """
        # Given
        mocked_last_published_at = mock.Mock()
        child_page = fake_page
        child_page.last_published_at = mocked_last_published_at

        # When
        timestamp = child_page.last_updated_at

        # Then
        assert timestamp == mocked_last_published_at

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
    @mock.patch.object(UKHSAPage, "_raise_error_if_slug_not_unique")
    def test_seo_title_field_is_required_by_clean_method_call(
        self,
        spy_raise_error_if_slug_not_unique: mock.MagicMock,
        fake_page: UKHSAPage,
    ):
        """
        Given a page model which inherits from `UKHSAPage`
        And no `seo_title` field was set
        When the `clean()` method is called
        Then a `ValidationError` is raised
        """
        # Given
        fake_page.seo_title = None

        # When / Then
        with pytest.raises(ValidationError):
            fake_page.clean()
