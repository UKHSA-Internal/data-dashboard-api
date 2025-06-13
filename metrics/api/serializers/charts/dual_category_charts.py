from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.api.serializers.charts.common import BaseChartsSerializer
from metrics.api.serializers.plots import PlotSerializer
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    ChartTypes,
)


class DualCategoryChartSegmentSerializer(serializers.Serializer):
    primary_field_values = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of primary field values for this segment",
        required=True,
        allow_empty=False,
    )
    secondary_field_value = serializers.CharField(
        help_text="Secondary field value for this segment",
        required=True,
    )
    color = serializers.ChoiceField(
        choices=RGBAChartLineColours.choices(),
        help_text="Color for this segment",
        required=True,
    )
    label = serializers.CharField(
        help_text="Label for this segment",
        required=False,
        allow_blank=True,
    )


class DualCategoryChartSerializer(BaseChartsSerializer):
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.selectable_choices(),
        required=True,
    )

    secondary_category = serializers.CharField(
        help_text="Secondary category field for the chart",
        required=True,
    )

    static_fields = PlotSerializer()

    segments = serializers.ListField(
        child=DualCategoryChartSegmentSerializer(),
        help_text="Segments for the dual category chart",
        required=True,
    )
