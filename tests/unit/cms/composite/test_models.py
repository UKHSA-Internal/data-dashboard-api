import pytest
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.admin.panels.inline_panel import InlinePanel
from wagtail.api.conf import APIField

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from tests.fakes.factories.cms.composite_page_factory import FakeCompositePageFactory


class TestCompositePage:
    @staticmethod
    def _retrieve_code_example_from_page_response(body) -> dict[str, str]:
        code_example = body[1].value
        code_snippet = code_example["content"][0].value

        return {
            "code_example": code_example,
            "code_snippet": code_snippet,
        }

    @staticmethod
    def _retrieve_code_example_from_page_template(body) -> dict[str, str]:
        code_example = body[1]["value"]
        code_snippet = body[1]["value"]["content"][0]["value"]

        return {
            "code_example": code_example,
            "code_snippet": code_snippet,
        }

    @pytest.mark.parametrize(
        "expected_api_fields",
        [
            "body",
            "date_posted",
            "last_published_at",
            "related_links_layout",
            "related_links",
            "seo_title",
            "search_description",
        ],
    )
    def test_has_correct_api_fields(self, expected_api_fields: str):
        """
        Given a blank `CompositePage` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeCompositePageFactory.build_blank_page()

        # When
        api_fields: list[APIField] = blank_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_fields in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel",
        [
            "body",
            "date_posted",
            "title",
            "page_description",
        ],
    )
    def test_has_correct_content_panels(self, expected_content_panel: str):
        """
        Given a blank `CompositePage` model
        When `content_panels` is called
        Then the expected names on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeCompositePageFactory.build_blank_page()

        # When
        content_panels: list[FieldPanel] = blank_page.content_panels

        # Then
        content_panel_names: set[str] = {p.field_name for p in content_panels}
        assert expected_content_panel in content_panel_names

    def test_has_correct_side_panels(self):
        """
        Given a blank `CompositePage` model
        When `sidebar_content_panels` is called
        Then the expected names are on the returned panel objects
        """
        # Given
        blank_page = FakeCompositePageFactory.build_blank_page()

        # When
        sidebar_content_panels: list[InlinePanel] = blank_page.sidebar_content_panels

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
        Given a blank `CompositePage` model
        When `is_previewable()` is called
        Then False is returned
        """
        # Given
        blank_page = FakeCompositePageFactory.build_blank_page()

        # When
        page_is_previewable: bool = blank_page.is_previewable()

        # Then
        assert not page_is_previewable

    def test_code_block_returns_correct_content(self):
        """
        Given a fake `CompositePage` model
        When a single code example is provided
        Then the `CompositePage` code example has been set correctly.
        """
        # Given
        template_page_name = "access_our_data_getting_started"
        access_our_data_child_page = open_example_page_response(
            page_name=template_page_name
        )
        fake_access_our_data_child_page = (
            FakeCompositePageFactory.build_page_from_template(
                page_name=template_page_name
            )
        )

        # When
        response = self._retrieve_code_example_from_page_response(
            body=fake_access_our_data_child_page.body
        )
        template = self._retrieve_code_example_from_page_template(
            body=access_our_data_child_page["body"]
        )

        # Then
        assert (
            response["code_example"]["heading"] == template["code_example"]["heading"]
        )
        assert (
            response["code_snippet"]["language"] == template["code_snippet"]["language"]
        )
        assert response["code_snippet"]["code"] == template["code_snippet"]["code"]
