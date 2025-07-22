from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
)
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters

FILE_FORMAT_CHOICES: list[str] = ["svg", "png", "jpg", "jpeg"]


class SubplotPlotSerializer(serializers.Serializer):
    label = serializers.CharField(required=True)
    colour = serializers.CharField(required=True)

    age = serializers.CharField(required=False)
    sex = serializers.CharField(required=False)
    stratum = serializers.CharField(required=False)
    geography_type = serializers.CharField(required=False)
    geography = serializers.CharField(required=False)


class SubPlotPlotsSerializer(serializers.ListSerializer):
    child = SubplotPlotSerializer()


class SubplotParametersSerializer(serializers.Serializer):
    metric = serializers.CharField(required=True)
    topic = serializers.CharField(required=True)
    stratum = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SubplotSerializer(serializers.Serializer):
    subplot_title = serializers.CharField(required=True)
    subplot_parameters = SubplotParametersSerializer(required=True)
    plots = SubPlotPlotsSerializer(required=True)


class SubplotsSerializer(serializers.ListSerializer):
    child = SubplotSerializer()


class ChartParametersSerializer(serializers.Serializer):
    theme = serializers.CharField(required=True)
    sub_theme = serializers.CharField(required=True)
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)

    age = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    stratum = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    geography_type = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    geography = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SubplotChartRequestSerializer(serializers.Serializer):
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
    x_axis_title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.CHART_X_AXIS_TITLE,
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

    chart_parameters = ChartParametersSerializer()
    subplots = SubplotsSerializer()

    def to_models(self, request: Request):
        return SubplotChartRequestParameters(**self.validated_data, request=request)
