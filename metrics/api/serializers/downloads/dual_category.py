from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.downloads.common import BaseDownloadsSerializer
from metrics.api.serializers.dual_category.common import (
    parse_dual_category_request,
    validate_dual_category_fields,
)
from metrics.api.serializers.plots import PlotSerializer
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
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
        return validate_dual_category_fields(attrs)

    def to_models(self, request: Request) -> DualCategoryDownloadRequestParams:
        request_context = parse_dual_category_request(
            data=self.data,
            static_fields=self.validated_data["static_fields"],
            chart_type=self.data.get("chart_type", "stacked_bar"),
        )

        return DualCategoryDownloadRequestParams(
            metric_group=request_context.metric_group,
            plots=request_context.plots,
            file_format=self.data["file_format"],
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis=request_context.x_axis,
            y_axis=request_context.y_axis,
            confidence_intervals=False,
            request=request,
            secondary_category=request_context.secondary_category,
            segment_secondary_values=request_context.segment_secondary_values,
            primary_field_values=request_context.primary_field_values,
        )
