from typing import Any

from caching.common.chart_block import is_dual_category_chart_block
from cms.dynamic_content.blocks_deconstruction import (
    CMS_COMPONENT_BLOCK_TYPE,
    CMSBlockParser,
)


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
