from typing import Any, List

from django.db.models import Manager
from django.db.utils import ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.charts.line_multi_coloured.colour_scheme import RGBAColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.models import ChartPlotParameters, ChartPlots
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import ChartAxisFields

DEFAULT_CHART_HEIGHT = 220
DEFAULT_CHART_WIDTH = 435


def get_axis_field_name(field: str) -> str:
    return str(getattr(ChartAxisFields, field, field))


DEFAULT_X_AXIS = ChartAxisFields.date.value
DEFAULT_Y_AXIS = ChartAxisFields.metric.value
GRAPH_AXIS_CHOICES: List[str] = [field.name for field in ChartAxisFields]


class ChartPlotSerializer(serializers.Serializer):
    # Required fields
    topic = serializers.ChoiceField(
        help_text=help_texts.TOPIC_FIELD,
        choices=[],
        required=True,
    )
    metric = serializers.ChoiceField(
        help_text=help_texts.METRIC_FIELD,
        choices=[],
        required=True,
    )
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.choices(),
        required=True,
    )

    # Optional fields
    stratum = serializers.CharField(
        help_text=help_texts.STRATUM_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    geography = serializers.CharField(
        help_text=help_texts.GEOGRAPHY_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    geography_type = serializers.CharField(
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    date_from = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        allow_null=True,
        default="",
    )
    date_to = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        allow_null=True,
        default="",
    )

    label = serializers.CharField(
        help_text=help_texts.LABEL_FIELD,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    line_colour = serializers.ChoiceField(
        choices=RGBAColours.choices(),
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

    def to_models(self):
        return ChartPlotParameters(**self.data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except (RuntimeError, ProgrammingError):
            pass
        # This is needed because the serializers are loaded by django at runtime
        # Because this is a child serializer, an `instance` must be passed
        # to the parent serializer.
        # Otherwise, we'd have to decorate all our unit tests with access to the db.

    def populate_choices(self):
        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields["metric"].choices = self.metric_manager.get_all_names()

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)


class ChartPlotsListSerializer(serializers.ListSerializer):
    child = ChartPlotSerializer()


FILE_FORMAT_CHOICES: List[str] = ["svg", "png", "jpg", "jpeg"]


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
        choices=GRAPH_AXIS_CHOICES,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.GRAPH_X_AXIS,
        default=DEFAULT_X_AXIS,
    )
    y_axis = serializers.ChoiceField(
        choices=GRAPH_AXIS_CHOICES,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=help_texts.GRAPH_Y_AXIS,
        default=DEFAULT_Y_AXIS,
    )

    plots = ChartPlotsListSerializer()

    def to_models(self) -> ChartPlots:
        return ChartPlots(
            plots=self.data["plots"],
            file_format=self.data["file_format"],
            chart_height=self.data["chart_height"] or DEFAULT_CHART_HEIGHT,
            chart_width=self.data["chart_width"] or DEFAULT_CHART_WIDTH,
            x_axis=get_axis_field_name(self.data["x_axis"] or DEFAULT_X_AXIS),
            y_axis=get_axis_field_name(self.data["y_axis"] or DEFAULT_Y_AXIS),
        )


class ChartsResponseSerializer(serializers.Serializer):
    chart = serializers.FileField(help_text=help_texts.CHARTS_RESPONSE_HELP_TEXT)
