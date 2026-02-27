import pytest
from wagtail.api.conf import APIField
from wagtail.admin.panels.field_panel import FieldPanel
from cms.acknowledgement.models import AcknowledgementPage


class TestAcknowledgementPage:
    # Every test starts with a blank `AcknowledgementPage` model
    blank_page = AcknowledgementPage

    @pytest.mark.parametrize(
        "expected_field_name",
        [
            "title",
            "body",
            "terms_of_service_link",
            "i_agree_checkbox",
            "disagree_button",
            "agree_button",
        ],
    )
    def test_has_correct_api_fields(self, expected_field_name: str):
        """
        Given a blank `AcknowledgementPage` model
        When `api_fields` is accessed
        Then the expected names are on the returned `APIField` objects
        """
        # When
        api_fields: list[APIField] = self.blank_page.api_fields
        api_field_names: set[str] = {api_field.name for api_field in api_fields}

        # Then
        assert expected_field_name in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel_field_name",
        [
            "body",
            "terms_of_service_link",
            "i_agree_checkbox",
            "disagree_button",
            "agree_button",
        ],
    )
    def test_has_correct_content_panels(self, expected_content_panel_field_name: str):
        """
        Given a blank `AcknowledgementPage` model
        When `content_panels` is accessed
        Then the expected field names exist on the `FieldPanel` definitions
        """
        # When
        content_panels = self.blank_page.content_panels
        panel_field_names = {
            panel.field_name
            for panel in content_panels
            if isinstance(panel, FieldPanel)
        }

        # Then
        assert expected_content_panel_field_name in panel_field_names

    def test_is_previewable_returns_false(self):
        """
        Given a blank `AcknowledgementPage` model
        When `is_previewable()` is called
        Then False is returned
        """
        # When
        page_is_previewable: bool = self.blank_page.is_previewable()

        # Then
        assert not page_is_previewable

    @pytest.mark.parametrize(
        "expected_seo_field_name",
        [
            "seo_change_frequency",
            "seo_priority",
        ],
    )
    def test_inherits_expected_seo_fields(self, expected_seo_field_name: str):
        """
        Given a blank `AcknowledgementPage` model
        When checking for SEO fields defined on the base class
        Then the expected fields exist on the concrete page model
        """
        # When / Then
        assert hasattr(self.blank_page, expected_seo_field_name)
