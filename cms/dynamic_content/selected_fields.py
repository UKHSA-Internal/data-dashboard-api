from typing import Any

from caching.common.chart_block import is_dual_category_chart_block
from cms.dynamic_content.blocks_deconstruction import (
    CMS_COMPONENT_BLOCK_TYPE,
    CMSBlockParser,
)

SELECTED_COMBINATION = tuple[str, str, str]


class CMSSelectedFieldParser:
    """Extracts the selected `theme` and `sub_theme` values from CMS chart blocks"""

    @classmethod
    def get_all_selected_theme_from_sections(
        cls, *, sections: list[dict[str, Any]]
    ) -> set[str]:
        """Extracts the selected themes from all chart blocks in the given `sections`."""
        return cls._get_all_selected_values_from_sections(
            sections=sections, field_name="theme"
        )

    @classmethod
    def get_all_selected_sub_theme_from_sections(
        cls, *, sections: list[dict[str, Any]]
    ) -> set[str]:
        """Extracts the selected sub-themes from all chart blocks in the given `sections`."""
        return cls._get_all_selected_values_from_sections(
            sections=sections, field_name="sub_theme"
        )

    @classmethod
    def _get_all_selected_values_from_sections(
        cls, *, sections: list[dict[str, Any]], field_name: str
    ) -> set[str]:
        chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE] = [
            chart_block
            for section in sections
            for chart_block in CMSBlockParser.get_all_chart_blocks_from_section(
                section=section
            )
        ]
        return cls._get_all_selected_values_from_chart_blocks(
            chart_blocks=chart_blocks, field_name=field_name
        )

    @classmethod
    def _get_all_selected_values_from_chart_blocks(
        cls, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE], field_name: str
    ) -> set[str]:
        values: set[str] = set()
        for block in chart_blocks:
            if is_dual_category_chart_block(block):
                fields_to_check = [block["static_fields"]]
            else:
                fields_to_check = [plot["value"] for plot in block["chart"]]

            for fields in fields_to_check:
                value = fields.get(field_name)
                if value:
                    values.add(value)

        return values

    @classmethod
    def get_all_selected_combinations_from_sections(
        cls, *, sections: list[dict[str, Any]]
    ) -> set[SELECTED_COMBINATION]:
        """Extracts the (topic, theme, sub_theme) combinations from all chart & headline blocks.

        The three values are read from the same plot / block at the same
        time, so they can never be mismatched. Headline blocks are included
        so that no topic selected on the page is lost.

        Where a topic has at least one complete combination, incomplete
        combinations for that same topic (e.g. from headline blocks with
        no theme) are dropped so they don't add noise.
        """
        chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE] = [
            chart_block
            for section in sections
            for chart_block in CMSBlockParser.get_all_chart_blocks_from_section(
                section=section
            )
        ]
        headline_blocks: list[CMS_COMPONENT_BLOCK_TYPE] = [
            headline_block
            for section in sections
            for headline_block in CMSBlockParser.get_all_headline_blocks_from_section(
                section=section
            )
        ]

        combinations = cls._get_combinations_from_chart_blocks(
            chart_blocks=chart_blocks
        ) | {cls._build_combination(block["value"]) for block in headline_blocks}

        return cls._drop_redundant_incomplete_combinations(combinations)

    @classmethod
    def _get_combinations_from_chart_blocks(
        cls, *, chart_blocks: list[CMS_COMPONENT_BLOCK_TYPE]
    ) -> set[SELECTED_COMBINATION]:
        combinations: set[SELECTED_COMBINATION] = set()
        for block in chart_blocks:
            if is_dual_category_chart_block(block):
                fields_to_check = [block["static_fields"]]
            else:
                fields_to_check = [plot["value"] for plot in block["chart"]]

            combinations.update(cls._build_combination(f) for f in fields_to_check)

        return combinations

    @staticmethod
    def _build_combination(fields: dict[str, Any]) -> SELECTED_COMBINATION:
        return (
            fields["topic"],
            fields.get("theme") or "",
            fields.get("sub_theme") or "",
        )

    @staticmethod
    def _drop_redundant_incomplete_combinations(
        combinations: set[SELECTED_COMBINATION],
    ) -> set[SELECTED_COMBINATION]:
        topics_with_complete_combination = {
            topic for topic, theme, sub_theme in combinations if theme and sub_theme
        }
        return {
            combination
            for combination in combinations
            if (combination[1] and combination[2])
            or combination[0] not in topics_with_complete_combination
        }
