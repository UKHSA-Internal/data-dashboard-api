import contextlib

from django.db.utils import OperationalError
from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts, plots
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    ChartTypes,
    DEFAULT_Y_AXIS_MINIMUM_VAlUE,
)
from metrics.domain.models import ChartRequestParams, PlotParameters


class ChartPlotSerializer(plots.PlotSerializer):
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.selectable_choices(),
        required=True,
    )

    label = serializers.CharField(
        help_text=help_texts.LABEL_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    line_colour = serializers.ChoiceField(
        choices=RGBAChartLineColours.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    line_type = serializers.ChoiceField(
        choices=ChartLineTypes.choices(),
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    use_smooth_lines = serializers.BooleanField(
        default=True, help_text=help_texts.CHART_USE_SMOOTH_LINES
    )
    use_markers = serializers.BooleanField(
        default=False, help_text=help_texts.CHART_USE_MARKERS
    )

    def to_models(self):
        return PlotParameters(**self.data)


class ChartPlotsListSerializer(serializers.ListSerializer):
    child = ChartPlotSerializer()

    def __init__(self, *args, **kwargs):
        with contextlib.suppress(OperationalError):
            super().__init__(*args, **kwargs)


FILE_FORMAT_CHOICES: list[str] = ["svg", "png", "jpg", "jpeg"]


class ChartsSerializer(serializers.Serializer):
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

    plots = ChartPlotsListSerializer()

    def to_models(self, request: Request) -> ChartRequestParams:
        x_axis = self.data.get("x_axis") or DEFAULT_X_AXIS
        y_axis = self.data.get("y_axis") or DEFAULT_Y_AXIS

        for plot in self.data["plots"]:
            plot["x_axis"] = x_axis
            plot["y_axis"] = y_axis

        return ChartRequestParams(
            plots=self.data["plots"],
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


class ChartsResponseSerializer(serializers.Serializer):
    chart = serializers.FileField(help_text=help_texts.CHARTS_RESPONSE)


class EncodedChartsRequestSerializer(ChartsSerializer):
    file_format = serializers.ChoiceField(
        choices=["svg"],
        help_text=help_texts.ENCODED_CHARTS_FILE_FORMAT_FIELD,
        default="svg",
    )


class EncodedChartResponseSerializer(serializers.Serializer):
    last_updated = serializers.CharField(
        help_text=help_texts.ENCODED_CHARTS_LAST_UPDATED,
        allow_blank=True,
    )
    chart = serializers.CharField(help_text=help_texts.ENCODED_CHARTS_RESPONSE)
    alt_text = serializers.CharField(help_text=help_texts.CHARTS_ALT_TEXT)
    figure = serializers.DictField(help_text=help_texts.CHARTS_FIGURE_OUTPUT)
