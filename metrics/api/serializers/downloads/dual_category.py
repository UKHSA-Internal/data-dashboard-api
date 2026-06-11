from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.downloads.common import BaseDownloadsSerializer
from metrics.api.serializers.plots import PlotSerializer
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    DataSourceFileType,
    extract_metric_group_from_metric,
)
from metrics.domain.models.downloads.dual_category import (
    DualCategoryDownloadRequestParams,
)


class DualCategoryDownloadSegmentSerializer(serializers.Serializer):
    secondary_field_value = serializers.CharField(required=True)
    colour = serializers.ChoiceField(
        choices=RGBAChartLineColours.choices(),
        required=False,
        allow_blank=True,
    )
    label = serializers.CharField(required=False, allow_blank=True, default="")


class DualCategoryDownloadSerializer(BaseDownloadsSerializer):
    chart_type = serializers.CharField(
        help_text=help_texts.CHART_TYPE_FIELD,
        required=False,
        default="stacked_bar",
    )
    primary_field_values = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )
    secondary_category = serializers.CharField(required=True)
    static_fields = PlotSerializer(required=True)
    segments = DualCategoryDownloadSegmentSerializer(many=True, required=True)

    @classmethod
    def validate(cls, attrs: dict) -> dict:
        """Validate primary field values based on the selected metric type.

        Args:
            attrs: Serializer attributes to validate.

        Returns:
            Validated attributes.
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
                    {
                        "x_axis": (
                            "This field should be set to 'date' for timeseries data."
                        )
                    }
                )

        elif not is_timeseries_data and not primary_field_values:
            raise serializers.ValidationError(
                {"primary_field_values": "This field is required for headline data."}
            )

        return attrs

    def to_models(self, request: Request) -> DualCategoryDownloadRequestParams:
        """Convert dual-category payload into plot queries for download.

        Args:
            request: Incoming API request.

        Returns:
            Dual-category download request parameters.
        """

        x_axis = self.data.get("x_axis") or DEFAULT_X_AXIS
        y_axis = self.data.get("y_axis") or DEFAULT_Y_AXIS
        primary_field_values = self.data.get("primary_field_values") or []
        secondary_category = self.data["secondary_category"]
        static_fields: dict = dict(self.validated_data["static_fields"])
        segments: list[dict] = self.data["segments"]
        chart_type = self.data.get("chart_type", "stacked_bar")
        segment_secondary_values = [
            segment["secondary_field_value"] for segment in segments
        ]

        if static_fields.get("date_from"):
            static_fields["date_from"] = static_fields["date_from"].isoformat()
        if static_fields.get("date_to"):
            static_fields["date_to"] = static_fields["date_to"].isoformat()

        metric_group = extract_metric_group_from_metric(metric=static_fields["metric"])
        is_timeseries_data = DataSourceFileType[metric_group].is_timeseries
        plots: list[dict] = []

        if is_timeseries_data:
            plots = [
                {
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "chart_type": chart_type,
                    **static_fields,
                    secondary_category: segment["secondary_field_value"],
                }
                for segment in segments
            ]
        else:
            for primary_field_value in primary_field_values:
                for segment in segments:
                    plots.append(
                        {
                            "x_axis": x_axis,
                            "y_axis": y_axis,
                            "chart_type": chart_type,
                            **static_fields,
                            x_axis: primary_field_value,
                            secondary_category: segment["secondary_field_value"],
                        }
                    )

        chart_request = DualCategoryDownloadRequestParams(
            metric_group=metric_group,
            plots=plots,
            file_format=self.data["file_format"],
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis=x_axis,
            y_axis=y_axis,
            confidence_intervals=False,
            request=request,
            secondary_category=secondary_category,
            segment_secondary_values=segment_secondary_values,
            primary_field_values=primary_field_values,
        )

        if is_timeseries_data:
            for plot in chart_request.plots:
                plot.override_y_axis_choice_to_none = True

        return chart_request
