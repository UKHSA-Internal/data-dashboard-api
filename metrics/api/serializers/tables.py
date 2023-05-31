from django.db.models import Manager
from django.db.utils import ProgrammingError
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.api.serializers.charts import (
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_X_AXIS,
    DEFAULT_Y_AXIS,
    GRAPH_AXIS_CHOICES,
    get_axis_field_name,
)
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.models import PlotsCollection
from metrics.domain.utils import ChartTypes


class TablePlotSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.TOPIC_FIELD,
    )
    metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.METRIC_FIELD,
    )
    chart_type = serializers.ChoiceField(
        help_text=help_texts.CHART_TYPE_FIELD,
        choices=ChartTypes.choices(),
        required=False,
        default="simple_line",
    )

    stratum = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.STRATUM_FIELD,
    )
    geography = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.GEOGRAPHY_FIELD,
    )
    geography_type = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
    )

    date_from = serializers.DateField(
        required=False,
        allow_null=True,
        default="",
        help_text=help_texts.DATE_FROM_FIELD,
    )
    date_to = serializers.DateField(
        required=False,
        allow_null=True,
        default="",
        help_text=help_texts.DATE_FROM_FIELD,
    )

    label = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
        help_text=help_texts.LABEL_FIELD,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except (RuntimeError, ProgrammingError):
            pass

    def populate_choices(self):
        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields["metric"].choices = self.metric_manager.get_all_names()

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)


class TablePlotsListSerializer(serializers.ListSerializer):
    child = TablePlotSerializer()


class TablesSerializer(serializers.Serializer):
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
    plots = TablePlotsListSerializer()

    def to_models(self) -> PlotsCollection:
        return PlotsCollection(
            plots=self.data["plots"],
            file_format="svg",
            chart_height=DEFAULT_CHART_HEIGHT,
            chart_width=DEFAULT_CHART_WIDTH,
            x_axis=get_axis_field_name(self.data["x_axis"] or DEFAULT_X_AXIS),
            y_axis=get_axis_field_name(self.data["y_axis"] or DEFAULT_Y_AXIS),
        )


class TablesResponseSerializer(serializers.Serializer):
    tabular_output = serializers.FileField(
        help_text=help_texts.TABLES_RESPONSE_HELP_TEXT
    )
