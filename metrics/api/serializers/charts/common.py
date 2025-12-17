from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
)

FILE_FORMAT_CHOICES: list[str] = ["svg", "png", "jpg", "jpeg"]


class BaseChartsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        help_text=help_texts.CHART_FILE_FORMAT_FIELD,
        default="svg",
    )
    chart_height = serializers.IntegerField(
        help_text=help_texts.CHART_HEIGHT,
        default=DEFAULT_CHART_HEIGHT,
        allow_null=True,
    )
    chart_width = serializers.IntegerField(
        help_text=help_texts.CHART_WIDTH,
        default=DEFAULT_CHART_WIDTH,
        allow_null=True,
    )
    x_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_X_AXIS,
        default=DEFAULT_X_AXIS,
    )
    x_axis_title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
    )
    y_axis = serializers.ChoiceField(
        choices=ChartAxisFields.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS,
        default=DEFAULT_Y_AXIS,
    )
    y_axis_title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.CHART_Y_AXIS_TITLE,
    )
    y_axis_minimum_value = serializers.DecimalField(
        required=False,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS_MINIMUM_VALUE,
        default=None,
        max_digits=10,
        decimal_places=1,
    )
    y_axis_maximum_value = serializers.DecimalField(
        required=False,
        allow_null=True,
        help_text=help_texts.CHART_Y_AXIS_MAXIMUM_VALUE,
        default=None,
        max_digits=10,
        decimal_places=1,
    )
    legend_title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.CHART_LEGEND_TITLE,
    )
    confidence_intervals = serializers.BooleanField(
        required=False,
        default=False,
        allow_null=True,
        help_text=help_texts.CHART_LEGEND_TITLE,  # TODO add help text
    )
    confidence_colour = serializers.ChoiceField(
        choices=RGBAChartLineColours.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
