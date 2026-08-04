from dataclasses import dataclass

from rest_framework import serializers

from metrics.domain.common.utils import (
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.tables.dual_category import build_dual_category_plot_params


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
    metric = attrs["static_fields"]["metric"]
    metric_group = extract_metric_group_from_metric(metric=metric)
    is_timeseries_data = DataSourceFileType[metric_group].is_timeseries

    if is_timeseries_data:
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
