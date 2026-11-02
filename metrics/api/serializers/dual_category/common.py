from dataclasses import dataclass

from rest_framework import serializers

from metrics.domain.common.utils import (
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    ChartTypes,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.tables.dual_category import build_dual_category_plot_params

REQUIRED_BUTTERFLY_SEGMENT_COUNT = 2


def validate_dual_category_fields(attrs: dict) -> dict:
    """
    Validate the fields for a dual category request.

    Args:
        attrs: The attributes to validate.

    Returns:
        The validated attributes.

    Raises:
        serializers.ValidationError: If the fields are invalid.
    """
    x_axis = attrs.get("x_axis") or DEFAULT_X_AXIS
    primary_field_values = attrs.get("primary_field_values") or []
    segments = attrs.get("segments") or []
    chart_type = attrs.get("chart_type") or "stacked_bar"
    is_butterfly_chart = chart_type == ChartTypes.butterfly.value
    metric = attrs["static_fields"]["metric"]
    metric_group = extract_metric_group_from_metric(metric=metric)
    is_timeseries_data = DataSourceFileType[metric_group].is_timeseries

    if is_butterfly_chart and len(segments) != REQUIRED_BUTTERFLY_SEGMENT_COUNT:
        raise serializers.ValidationError(
            {
                "segments": (
                    "Butterfly charts require exactly "
                    f"{REQUIRED_BUTTERFLY_SEGMENT_COUNT} segments, "
                    f"one for each side of the chart. Got {len(segments)}."
                )
            }
        )

    # Butterfly charts always plot a primary category (eg. age) against
    # a secondary category (eg. stratum), regardless of whether the
    # underlying metric is sourced from headline or timeseries data.
    if is_timeseries_data and not is_butterfly_chart:
        if primary_field_values:
            raise serializers.ValidationError(
                {
                    "primary_field_values": (
                        "This field should not be provided for timeseries data."
                    )
                }
            )
        if x_axis != ChartAxisFields.date.name:
            raise serializers.ValidationError(
                {"x_axis": ("This field should be set to 'date' for timeseries data.")}
            )
    elif not primary_field_values:
        raise serializers.ValidationError(
            {"primary_field_values": "This field is required for headline data."}
        )

    return attrs


@dataclass(frozen=True)
class DualCategoryRequestContext:
    x_axis: str
    y_axis: str
    primary_field_values: list[str]
    secondary_category: str
    static_fields: dict
    segments: list[dict]
    chart_type: str
    segment_secondary_values: list[str]
    metric_group: str
    is_timeseries_data: bool
    plots: list[dict]


def parse_dual_category_request(
    *,
    data: dict,
    static_fields: dict,
    chart_type: str,
) -> DualCategoryRequestContext:
    x_axis = data.get("x_axis") or DEFAULT_X_AXIS
    y_axis = data.get("y_axis") or DEFAULT_Y_AXIS

    if chart_type == ChartTypes.butterfly.value:
        # Butterfly charts draw horizontal bars, so callers describe the axes
        # as they appear on the chart: the horizontal (x) axis holds the metric
        # values and the vertical (y) axis holds the primary category (eg. age).
        # Internally the primary category is always carried on `x_axis`, so the
        # pair is swapped back here, matching `DualCategoryChartSerializer`.
        x_axis, y_axis = y_axis, x_axis

    primary_field_values = data.get("primary_field_values") or []
    secondary_category = data["secondary_category"]
    segments: list[dict] = data["segments"]
    segment_secondary_values = [
        segment["secondary_field_value"] for segment in segments
    ]

    if static_fields.get("date_from"):
        static_fields["date_from"] = static_fields["date_from"].isoformat()
    if static_fields.get("date_to"):
        static_fields["date_to"] = static_fields["date_to"].isoformat()

    metric_group = extract_metric_group_from_metric(metric=static_fields["metric"])
    is_timeseries_data = DataSourceFileType[metric_group].is_timeseries
    plots = build_dual_category_plot_params(
        x_axis=x_axis,
        y_axis=y_axis,
        chart_type=chart_type,
        static_fields=static_fields,
        segments=segments,
        secondary_category=secondary_category,
        primary_field_values=primary_field_values,
        is_timeseries_data=is_timeseries_data,
    )

    return DualCategoryRequestContext(
        x_axis=x_axis,
        y_axis=y_axis,
        primary_field_values=primary_field_values,
        secondary_category=secondary_category,
        static_fields=static_fields,
        segments=segments,
        chart_type=chart_type,
        segment_secondary_values=segment_secondary_values,
        metric_group=metric_group,
        is_timeseries_data=is_timeseries_data,
        plots=plots,
    )
