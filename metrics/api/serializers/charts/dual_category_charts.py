from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.charts.common import BaseChartsSerializer
from metrics.api.serializers.plots import PlotSerializer
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartTypes,
    DEFAULT_Y_AXIS_MINIMUM_VAlUE,
)
from metrics.domain.models.charts.dual_category_charts import DualCategoryChartRequestParams


class DualCategoryChartSegmentSerializer(serializers.Serializer):
    secondary_field_value = serializers.CharField(
        help_text="Secondary field value for this segment",
        required=True,
    )
    colour = serializers.ChoiceField(
        choices=RGBAChartLineColours.choices(),
        help_text="Color for this segment",
        required=True,
    )
    label = serializers.CharField(
        help_text="Label for this segment",
        required=False,
        allow_blank=True,
    )


class StaticFieldsSerializer(PlotSerializer):
    theme = serializers.CharField(
        required=True,
        allow_blank=True,
        allow_null=True,
    )
    sub_theme = serializers.CharField(
        required=True,
        allow_blank=True,
        allow_null=True,
    )


class DualCategoryChartSerializer(BaseChartsSerializer):
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.dual_category_chart_options(),
        required=True,
    )
    primary_field_values = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of primary field values for this segment",
        required=True,
        allow_empty=False,
    )

    secondary_category = serializers.CharField(
        help_text="Secondary category field for the chart",
        required=True,
    )

    static_fields = StaticFieldsSerializer()

    segments = serializers.ListField(
        child=DualCategoryChartSegmentSerializer(),
        help_text="Segments for the dual category chart",
        required=True,
    )

    def to_models(self, request: Request) -> DualCategoryChartRequestParams:
        x_axis = self.data.get("x_axis") or DEFAULT_X_AXIS
        y_axis = self.data.get("y_axis") or DEFAULT_Y_AXIS

        primary_field_values = self.data.get("primary_field_values")
        static_fields: dict[str, str | int] = self.validated_data.pop("static_fields")

        if static_fields["date_to"]:
            static_fields["date_to"] = static_fields["date_to"].isoformat()

        if static_fields["date_from"]:
            static_fields["date_from"] = static_fields["date_from"].isoformat()

        groups_plots = []

        for primary_field_value in primary_field_values:
            for segment in self.data["segments"]:
                plot = {
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "line_colour": segment["colour"],
                    **static_fields,
                    x_axis: primary_field_value,
                    self.data.get("secondary_category"): segment["secondary_field_value"],
                }
                groups_plots.append(plot)

        return DualCategoryChartRequestParams(
            chart_type=self.data["chart_type"],
            primary_field_values=self.data["primary_field_values"],
            secondary_category=self.data["secondary_category"],
            static_fields=self.data["static_fields"],
            plots=groups_plots,
            file_format=self.data["file_format"],
            chart_height=self.data["chart_height"] or DEFAULT_CHART_HEIGHT,
            chart_width=self.data["chart_width"] or DEFAULT_CHART_WIDTH,
            x_axis=x_axis,
            y_axis=y_axis,
            x_axis_title=self.data.get("x_axis_title", ""),
            y_axis_title=self.data.get("y_axis_title", ""),
            y_axis_minimum_value=self.data["y_axis_minimum_value"]
            or DEFAULT_Y_AXIS_MINIMUM_VAlUE,
            y_axis_maximum_value=self.data["y_axis_maximum_value"],
            request=request,
        )
