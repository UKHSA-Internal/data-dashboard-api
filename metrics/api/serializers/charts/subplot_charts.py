from decimal import Decimal

from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_Y_AXIS_MINIMUM_VAlUE,
)
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters

FILE_FORMAT_CHOICES: list[str] = ["svg", "png", "jpg", "jpeg", "json", "csv"]


class SubplotPlotSerializer(serializers.Serializer):
    label = serializers.CharField(required=True)
    line_colour = serializers.CharField(required=True)

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
    theme = serializers.CharField(required=False)
    sub_theme = serializers.CharField(required=False)

    def validate(self, data):
        """
        Check that theme and sub_theme are present at either
        chart_parameters or subplot_parameters level
        """
        chart_params = self.parent.parent.parent.initial_data['chart_parameters']
        chart_theme = chart_params.get('theme')
        chart_sub_theme = chart_params.get('sub_theme')
        subplot_theme = data.get('theme')
        subplot_sub_theme = data.get('sub_theme')
        if not subplot_theme and not chart_theme:
            raise serializers.ValidationError(
                "'theme' must be specified at either "
                "subplot_parameters or chart_parameters level"
            )
        if not subplot_sub_theme and not chart_sub_theme:
            raise serializers.ValidationError(
                "'sub_theme' must be specified at either "
                "subplot_parameters or chart_parameters level"
            )
        return data


class SubplotSerializer(serializers.Serializer):
    subplot_title = serializers.CharField(required=True)
    subplot_parameters = SubplotParametersSerializer(required=True)
    plots = SubPlotPlotsSerializer(required=True)


class SubplotsSerializer(serializers.ListSerializer):
    child = SubplotSerializer()


class MetricRangeSerializer(serializers.Serializer):
    start = serializers.DecimalField(max_digits=20, decimal_places=5)
    end = serializers.DecimalField(max_digits=20, decimal_places=5)


class ChartParametersSerializer(serializers.Serializer):
    x_axis = serializers.CharField(required=True)
    y_axis = serializers.CharField(required=True)
    theme = serializers.CharField(required=False)
    sub_theme = serializers.CharField(required=False)
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)

    age = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    stratum = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    geography_type = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    geography = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    metric_value_ranges = MetricRangeSerializer(
        many=True, allow_null=True, required=False
    )


SUBPLOT_CHART_PARAMETER_PAYLOAD_TYPE = dict[str, str]
SUBPLOT_PARAMETERS = dict[str, str]


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
    target_threshold = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=10,
        decimal_places=2,
    )
    target_threshold_label = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    chart_parameters = ChartParametersSerializer()
    subplots = SubplotsSerializer()

    def to_models(self, request: Request) -> SubplotChartRequestParameters:
        """
        chart_parameters is used to reduce the duplication of data entry for content editors
        for the chart request its really a part of the `subplot_parameters`. Its the combination
        of these two objects that when added to the `plot` fields make the request.
        """
        chart_parameters: SUBPLOT_CHART_PARAMETER_PAYLOAD_TYPE = (
            self.validated_data.pop("chart_parameters")
        )

        if chart_parameters["date_from"]:
            chart_parameters["date_from"] = chart_parameters["date_from"].isoformat()

        if chart_parameters["date_to"]:
            chart_parameters["date_to"] = chart_parameters["date_to"].isoformat()

        provided_metric_value_ranges = chart_parameters.pop("metric_value_ranges", [])
        metric_value_ranges: list[tuple[Decimal, Decimal]] = [
            (metric_value_range.get("start"), metric_value_range.get("end"))
            for metric_value_range in provided_metric_value_ranges
        ]

        for subplot in self.validated_data["subplots"]:
            subplot_parameters = subplot.pop("subplot_parameters")
            subplot["x_axis"] = chart_parameters["x_axis"]
            subplot["y_axis"] = chart_parameters["y_axis"]

            for plot in subplot["plots"]:
                plot.update(
                    {
                        **chart_parameters,
                        **subplot_parameters,
                    }
                )
                plot["metric_value_ranges"] = metric_value_ranges

        return SubplotChartRequestParameters(
            file_format=self.validated_data["file_format"],
            chart_height=self.validated_data["chart_height"] or DEFAULT_CHART_HEIGHT,
            chart_width=self.validated_data["chart_width"] or DEFAULT_CHART_WIDTH,
            x_axis_title=self.validated_data["x_axis_title"],
            y_axis_title=self.validated_data["y_axis_title"],
            y_axis_minimum_value=self.validated_data["y_axis_minimum_value"]
            or DEFAULT_Y_AXIS_MINIMUM_VAlUE,
            y_axis_maximum_value=self.validated_data["y_axis_maximum_value"],
            target_threshold=self.validated_data.get("target_threshold", None),
            target_threshold_label=self.validated_data.get(
                "target_threshold_label", None
            ),
            subplots=self.validated_data["subplots"],
            request=request,
        )


class ChartPreviewQueryParamsSerializer(serializers.Serializer):
    preview = serializers.BooleanField(required=False)
