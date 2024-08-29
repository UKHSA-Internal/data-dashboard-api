import pytest
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.api.conf import APIField

from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory


class TestBlankCommonPage:

    @pytest.mark.parametrize(
        "expected_api_field_name",
        [
            "body",
            "date_posted",
            "last_published_at",
            "related_links",
            "seo_title",
            "search_description",
        ],
    )
    def test_has_correct_api_fields(self, expected_api_field_name: str):
        """
        Given a blank `CommonPage` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeCommonPageFactory.build_blank_page()

        # When
        api_fields: list[APIField] = blank_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field_name in api_field_names

    def test_has_correct_content_panels(self):
        """
        Given a blank `CommonPage` model
        When `content_panels` is called
        Then the expected names are on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeCommonPageFactory.build_blank_page()

        # When
        content_panels: list[FieldPanel] = blank_page.content_panels

        # Then
        expected_content_panel_names: set[str] = {
            "title",
            "date_posted",
            "body",
        }
        content_panel_names: set[str] = {p.field_name for p in content_panels}
        assert content_panel_names == expected_content_panel_names

    def test_has_correct_sidebar_panels(self):
        """
        Given a blank `CommonPage` model
        When `sidebar_content_panels` is called
        Then the expected names are on the returned `InlinePanel` objects
        """
        # Given
        blank_page = FakeCommonPageFactory.build_blank_page()

        # When
        sidebar_content_panels = blank_page.sidebar_content_panels

        # Then
        expected_sidebar_content_panel_names: set[str] = {
            "related_links",
            "related_links_layout",
        }
        sidebar_content_panel_names: set[str] = {
            p.clean_name for p in sidebar_content_panels
        }
        assert sidebar_content_panel_names == expected_sidebar_content_panel_names

    def test_is_previewable_returns_false(self):
        """
        Given a blank `CommonPage` model
        When `is_previewable()` is called
        Then False is returned
        """
        # Given
        blank_page = FakeCommonPageFactory.build_blank_page()

        # When
        page_is_previewable: bool = blank_page.is_previewable()

        # Then
        assert not page_is_previewable
