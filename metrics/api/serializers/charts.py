from typing import List

from django.db.models import Manager
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.models import PlotParameters, PlotsCollection
from metrics.domain.utils import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    ChartAxisFields,
    ChartTypes,
)


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

    def to_models(self):
        return PlotParameters(**self.data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except (RuntimeError, ProgrammingError, OperationalError):
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

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except OperationalError:
            pass


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

    plots = ChartPlotsListSerializer()

    def to_models(self) -> PlotsCollection:
        for plot in self.data["plots"]:
            plot["x_axis"] = plot.get("x_axis") or DEFAULT_X_AXIS
            plot["y_axis"] = plot.get("y_axis") or DEFAULT_Y_AXIS

        return PlotsCollection(
            plots=self.data["plots"],
            file_format=self.data["file_format"],
            chart_height=self.data["chart_height"] or DEFAULT_CHART_HEIGHT,
            chart_width=self.data["chart_width"] or DEFAULT_CHART_WIDTH,
        )


class ChartsResponseSerializer(serializers.Serializer):
    chart = serializers.FileField(help_text=help_texts.CHARTS_RESPONSE_HELP_TEXT)


class EncodedChartResponseSerializer(serializers.Serializer):
    last_updated = serializers.CharField(
        help_text=help_texts.ENCODED_CHARTS_LAST_UPDATED_HELP_TEXT,
        allow_blank=True,
    )
    chart = serializers.CharField(
        help_text=help_texts.ENCODED_CHARTS_RESPONSE_HELP_TEXT
    )
