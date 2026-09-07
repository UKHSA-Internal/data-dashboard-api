from unittest.mock import patch, MagicMock

import pytest
from django.core.exceptions import ValidationError

from cms.auth_content.models.non_public_page import (
    NonPublicCapablePage,
    DataClassificationLevels,
    get_non_public_page_types,
)
from cms.metrics_documentation.models import MetricsDocumentationChildEntry
from cms.topic.models import TopicPage


def create_non_public_page(*args, **kwargs) -> NonPublicCapablePage:
    class MockNonPublicCapablePage(NonPublicCapablePage):
        class Meta:
            app_label = "data"

    return MockNonPublicCapablePage(*args, **kwargs)


class TestNonPublicPage:

    def test_is_abstract_model(self):
        assert NonPublicCapablePage._meta.abstract == True

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "is_public",
            "non_public_page_options",
        ],
    )
    def test_default_content_panels(self, expected_content_panel_name: str):
        assert expected_content_panel_name in [
            panel.clean_name for panel in NonPublicCapablePage.content_panels
        ]

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "page_classification",
            "page_theme",
            "page_sub_theme",
            "page_topic",
        ],
    )
    def test_default_options_panels(self, expected_content_panel_name: str):
        non_public_page_options_panel = next(
            (
                panel
                for panel in NonPublicCapablePage.content_panels
                if panel.clean_name == "non_public_page_options"
            ),
            None,
        )
        assert (
            non_public_page_options_panel is not None
        ), "non_public_page_options panel not found"

        assert expected_content_panel_name in [
            panel.clean_name for panel in non_public_page_options_panel.children
        ]

    @pytest.mark.parametrize(
        "expected_api_field_name",
        [
            "is_public",
            "page_classification",
        ],
    )
    def test_default_api_fields(self, expected_api_field_name: str):
        assert expected_api_field_name in [
            panel.name for panel in NonPublicCapablePage.api_fields
        ]

    def test_clean_public_page(self):
        page = create_non_public_page(is_public=True)
        reset_for_public_page_mock = MagicMock()
        validate_non_public_page_mock = MagicMock()
        with patch.object(page, "_reset_for_public_page", reset_for_public_page_mock):
            with patch.object(
                page, "_validate_non_public_page", validate_non_public_page_mock
            ):
                page.clean()
                reset_for_public_page_mock.assert_called_once()
                validate_non_public_page_mock.assert_not_called()

    def test_clean_non_public_page(self):
        page = create_non_public_page(is_public=False)
        reset_for_public_page_mock = MagicMock()
        validate_non_public_page_mock = MagicMock()
        with patch.object(page, "_reset_for_public_page", reset_for_public_page_mock):
            with patch.object(
                page, "_validate_non_public_page", validate_non_public_page_mock
            ):
                page.clean()
                reset_for_public_page_mock.assert_not_called()
                validate_non_public_page_mock.assert_called_once()

    def test_reset_for_public_page(self):
        page = create_non_public_page(
            is_public=True,
            page_classification=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
            page_theme="1",
            page_sub_theme="2",
            page_topic="3",
        )
        page._reset_for_public_page()
        assert page.is_public
        assert page.page_classification == ""
        assert page.page_theme == ""
        assert page.page_sub_theme == ""
        assert page.page_topic == ""

    @pytest.mark.parametrize("classification", ["", None])
    def test_validate_non_public_page_invalid_classification(
        self, classification: str | None
    ):
        page = create_non_public_page(
            is_public=True,
            page_classification=classification,
            page_theme="1",
            page_sub_theme="2",
            page_topic="3",
        )
        with pytest.raises(ValidationError) as e:
            page._validate_non_public_page()
        assert "Please select a classification level for this non-public page" in str(
            e.value
        )

    @pytest.mark.parametrize("theme", ["", None])
    def test_validate_non_public_page_invalid_theme(self, theme: str | None):
        page = create_non_public_page(
            is_public=True,
            page_classification=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
            page_theme=theme,
            page_sub_theme="2",
            page_topic="3",
        )
        with pytest.raises(ValidationError) as e:
            page._validate_non_public_page()
        assert "Please select a theme for this non-public page" in str(e.value)

    @pytest.mark.parametrize("sub_theme", ["", None])
    def test_validate_non_public_page_invalid_sub_theme(self, sub_theme: str | None):
        page = create_non_public_page(
            is_public=True,
            page_classification=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
            page_theme="1",
            page_sub_theme=sub_theme,
            page_topic="3",
        )
        with pytest.raises(ValidationError) as e:
            page._validate_non_public_page()
        assert "Please select a sub theme for this non-public page" in str(e.value)

    @pytest.mark.parametrize("topic", ["", None])
    def test_validate_non_public_page_invalid_topic(self, topic: str | None):
        page = create_non_public_page(
            is_public=True,
            page_classification=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
            page_theme="1",
            page_sub_theme="2",
            page_topic=topic,
        )
        with pytest.raises(ValidationError) as e:
            page._validate_non_public_page()
        assert "Please select a topic for this non-public page" in str(e.value)


class TestGetNonPublicPageTypes:

    def test_list_contains_expected_pages(self):
        pages = get_non_public_page_types()
        assert TopicPage in pages
        assert MetricsDocumentationChildEntry in pages

        real_pages = [page for page in pages if not page.__module__.startswith("test")]
        assert len(real_pages) == 2
