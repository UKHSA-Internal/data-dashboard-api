import pytest
from wagtail.api.conf import APIField
from wagtail.admin.panels.field_panel import FieldPanel
from cms.acknowledgement.models import AcknowledgementPage


class TestAcknowledgementPage:
    """
    Given a blank acknowledgement page (for every test)
    """

    blank_page = AcknowledgementPage

    @pytest.mark.parametrize(
        "expected_field_name",
        [
            "title",
            "body",
            "terms_of_service_link",
            "terms_of_service_error",
            "i_agree_checkbox",
            "disagree_button",
            "agree_button",
        ],
    )
    def test_has_correct_api_fields(self, expected_field_name: str):
        """
        When the declared API fields of the page are accessed
        Then the expected API fields are present
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
            "terms_of_service_error",
            "i_agree_checkbox",
            "disagree_button",
            "agree_button",
        ],
    )
    def test_has_correct_content_panels(self, expected_content_panel_field_name: str):
        """
        When the declared content panels of the page are accessed
        Then the expected content panels are present
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
        When the declared preview behavior of the page is accessed
        Then false is returned
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
        When checking for the declared SEO fields of the page
        Then the expected SEO fields are present
        """
        # When / Then
        assert hasattr(self.blank_page, expected_seo_field_name)
