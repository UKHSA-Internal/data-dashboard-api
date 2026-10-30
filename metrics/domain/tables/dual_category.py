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
    # Butterfly charts always plot a primary category (eg. age) against
    # a secondary category, so they follow the same grouping as headline
    # data, even when the underlying metric is sourced from timeseries data.
    if is_timeseries_data and chart_type != "butterfly":
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
            "x_axis": x_axis,
            "y_axis": y_axis,
            "chart_type": chart_type,
            **static_fields,
            x_axis: primary_field_value,
            secondary_category: segment["secondary_field_value"],
            "label": segment.get("label") or segment["secondary_field_value"],
        }
        for primary_field_value in primary_field_values
        for segment in segments
    ]
