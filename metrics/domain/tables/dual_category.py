from metrics.domain.chart_axis_groups import pick_axis


def build_dual_category_plot_params(
    *,
    x_axis: str,
    y_axis: str,
    chart_type: str,
    static_fields: dict,
    segments: list[dict],
    secondary_category: str,
    primary_field_values: list[str],
    is_timeseries_data: bool,
) -> list[dict]:
    if is_timeseries_data:
        return [
            {
                "x_axis": x_axis,
                "y_axis": y_axis,
                "chart_type": chart_type,
                **static_fields,
                secondary_category: segment["secondary_field_value"],
                "label": segment.get("label") or segment["secondary_field_value"],
            }
            for segment in segments
        ]

    return [
        {
            "x_axis": y_axis,
            "y_axis": x_axis,
            "chart_type": chart_type,
            **static_fields,
            pick_axis(chart_type, x_axis, y_axis): primary_field_value,
            secondary_category: segment["secondary_field_value"],
            "label": segment.get("label") or segment["secondary_field_value"],
        }
        for primary_field_value in primary_field_values
        for segment in segments
    ]
