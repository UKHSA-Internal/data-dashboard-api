from unittest import mock

import pytest

from cms.dynamic_content.selected_fields import CMSSelectedFieldParser

MODULE_PATH = "cms.dynamic_content.selected_fields"


class TestCMSSelectedFieldParser:
    @staticmethod
    def _build_standard_block(*plot_values: dict) -> dict:
        return {"chart": [{"value": value} for value in plot_values]}

    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=False)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_collects_unique_values_from_standard_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock, mock_is_dual: mock.MagicMock
    ):
        """
        Given chart blocks whose plots select themes and sub themes
        When the `*_from_sections()` methods are called
        Then the unique values are returned as sets of strings
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            self._build_standard_block(
                {"theme": "infectious_disease", "sub_theme": "respiratory"},
                {"theme": "infectious_disease", "sub_theme": "respiratory"},
            ),
            self._build_standard_block(
                {"theme": "extreme_event", "sub_theme": "weather_alert"},
            ),
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )
        sub_themes = CMSSelectedFieldParser.get_all_selected_sub_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease", "extreme_event"}
        assert sub_themes == {"respiratory", "weather_alert"}

    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=True)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_reads_static_fields_for_dual_category_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock, mock_is_dual: mock.MagicMock
    ):
        """
        Given a dual category chart block
        When `get_all_selected_theme_from_sections()` is called
        Then the theme is read from the block's `static_fields`
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            {
                "static_fields": {
                    "theme": "infectious_disease",
                    "sub_theme": "respiratory",
                }
            }
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease"}

    @pytest.mark.parametrize("empty_value", [None, ""])
    @mock.patch(f"{MODULE_PATH}.is_dual_category_chart_block", return_value=False)
    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_skips_missing_or_empty_values(
        self,
        spy_cms_block_parser: mock.MagicMock,
        mock_is_dual: mock.MagicMock,
        empty_value,
    ):
        """
        Given plots with a missing, None or empty theme
        When `get_all_selected_theme_from_sections()` is called
        Then those plots are skipped
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = [
            self._build_standard_block(
                {"theme": empty_value},
                {},
                {"theme": "infectious_disease"},
            )
        ]

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == {"infectious_disease"}

    @mock.patch(f"{MODULE_PATH}.CMSBlockParser")
    def test_returns_empty_set_when_there_are_no_chart_blocks(
        self, spy_cms_block_parser: mock.MagicMock
    ):
        """
        Given sections which contain no chart blocks
        When `get_all_selected_theme_from_sections()` is called
        Then an empty set is returned
        """
        # Given
        spy_cms_block_parser.get_all_chart_blocks_from_section.return_value = []

        # When
        themes = CMSSelectedFieldParser.get_all_selected_theme_from_sections(
            sections=[{}]
        )

        # Then
        assert themes == set()
