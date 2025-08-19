from rest_framework import serializers
from rest_framework.request import Request

from metrics.api.serializers import help_texts
from metrics.domain.common.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_Y_AXIS_MINIMUM_VAlUE,
)
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters

FILE_FORMAT_CHOICES: list[str] = ["svg", "png", "jpg", "jpeg"]


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


class SubplotSerializer(serializers.Serializer):
    subplot_title = serializers.CharField(required=True)
    subplot_parameters = SubplotParametersSerializer(required=True)
    plots = SubPlotPlotsSerializer(required=True)


class SubplotsSerializer(serializers.ListSerializer):
    child = SubplotSerializer()


class ChartParametersSerializer(serializers.Serializer):
    x_axis = serializers.CharField(required=True)
    y_axis = serializers.CharField(required=True)
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
        of these two objects that when addewd to the `plot` fields make the request.
        """
        chart_parameters: SUBPLOT_CHART_PARAMETER_PAYLOAD_TYPE = (
            self.validated_data.pop("chart_parameters")
        )

        if chart_parameters["date_from"]:
            chart_parameters["date_from"] = chart_parameters["date_from"].isoformat()

        if chart_parameters["date_to"]:
            chart_parameters["date_to"] = chart_parameters["date_to"].isoformat()

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

        return SubplotChartRequestParameters(
            file_format=self.validated_data["file_format"],
            chart_height=self.validated_data["chart_height"] or DEFAULT_CHART_HEIGHT,
            chart_width=self.validated_data["chart_width"] or DEFAULT_CHART_WIDTH,
            x_axis_title=self.validated_data["x_axis_title"],
            y_axis_title=self.validated_data["y_axis_title"],
            y_axis_minimum_value=self.validated_data["y_axis_minimum_value"]
            or DEFAULT_Y_AXIS_MINIMUM_VAlUE,
            y_axis_maximum_value=self.validated_data["y_axis_maximum_value"],
            target_threshold=self.validated_data["target_threshold"],
            target_threshold_label=self.validated_data["target_threshold_label"],
            subplots=self.validated_data["subplots"],
            request=request,
        )


class ChartPreviewQueryParamsSerializer(serializers.Serializer):
    preview = serializers.BooleanField(required=False)
