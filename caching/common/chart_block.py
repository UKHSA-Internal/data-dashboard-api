CMS_COMPONENT_BLOCK_TYPE = dict[str, str | dict[str, str] | list[dict[str, str]]]


def is_dual_category_chart_block(chart_block: CMS_COMPONENT_BLOCK_TYPE) -> bool:
    """
    Check if a chart block is a dual category chart block.

    Args:
        chart_block (CMS_COMPONENT_BLOCK_TYPE): The chart block to check.

       Returns:
           bool: True if the chart block is a dual category chart block, False otherwise.
    """

    has_axes_fields = (
        chart_block.get("x_axis") is not None
        or chart_block.get("primary_field_values") is not None
    )
    return (
        has_axes_fields
        and chart_block.get("chart_type") == "stacked_bar"
        and chart_block.get("segments") is not None
    )
