from typing import List, Set

from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.admin.panels.inline_panel import InlinePanel
from wagtail.api.conf import APIField

from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory


class TestBlankHomePage:
    def test_has_correct_api_fields(self):
        """
        Given a blank `HomePage` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        api_fields: List[APIField] = blank_page.api_fields

        # Then
        expected_api_field_names: Set[str] = {
            "page_description",
            "body",
            "related_links",
            "last_published_at",
        }
        api_field_names: Set[str] = {api_field.name for api_field in api_fields}
        assert api_field_names == expected_api_field_names

    def test_has_correct_content_panels(self):
        """
        Given a blank `HomePage` model
        When `content_panels` is called
        Then the expected names are on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        content_panels: List[FieldPanel] = blank_page.content_panels

        # Then
        expected_content_panel_names: Set[str] = {
            "title",
            "page_description",
            "body",
        }
        content_panel_names: Set[str] = {p.field_name for p in content_panels}
        assert content_panel_names == expected_content_panel_names

    def test_has_correct_sidebar_panels(self):
        """
        Given a blank `HomePage` model
        When `sidebar_content_panels` is called
        Then the expected names are on the returned `InlinePanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        sidebar_content_panels: List[InlinePanel] = blank_page.sidebar_content_panels

        # Then
        expected_sidebar_content_panel_names: Set[str] = {
            "related_links",
        }
        sidebar_content_panel_names: Set[str] = {
            p.relation_name for p in sidebar_content_panels
        }
        assert sidebar_content_panel_names == expected_sidebar_content_panel_names
