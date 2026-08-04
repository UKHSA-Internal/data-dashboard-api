from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.api.serializers.charts.dual_category_charts import (
    DualCategoryChartSerializer,
)
from metrics.api.serializers.downloads.dual_category import (
    DualCategoryDownloadSegmentSerializer,
)
from metrics.api.serializers.dual_category.common import parse_dual_category_request
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    ChartTypes,
)
from metrics.domain.models.tables.dual_category import DualCategoryTableRequestParams


class DualCategoryTableRequestParamsSerializer(DualCategoryChartSerializer):
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.choices(),
        required=False,
        default="stacked_bar",
    )
    x_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_X_AXIS,
        default=DEFAULT_X_AXIS,
    )
    y_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS,
        default=DEFAULT_Y_AXIS,
    )
    segments = DualCategoryDownloadSegmentSerializer(many=True, required=True)

    def to_models(self, request: Request) -> DualCategoryTableRequestParams:
        request_context = parse_dual_category_request(
            data=self.data,
            static_fields=self.validated_data["static_fields"],
            chart_type=self.data.get("chart_type", "stacked_bar"),
        )

        return DualCategoryTableRequestParams(
            metric_group=request_context.metric_group,
            plots=request_context.plots,
            file_format=self.data.get("file_format", "svg"),
            chart_height=self.data.get("chart_height") or DEFAULT_CHART_HEIGHT,
            chart_width=self.data.get("chart_width") or DEFAULT_CHART_WIDTH,
            x_axis=request_context.x_axis,
            y_axis=request_context.y_axis,
            request=request,
            secondary_category=request_context.secondary_category,
            segment_secondary_values=request_context.segment_secondary_values,
            primary_field_values=request_context.primary_field_values,
        )
