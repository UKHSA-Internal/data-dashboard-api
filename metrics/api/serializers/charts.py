from typing import List

from django.db.models import Manager
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic
from metrics.domain.models import ChartPlots, ChartsPlotParameters
from metrics.domain.utils import ChartTypes

FILE_FORMAT_CHOICES: List[str] = ["svg", "png", "jpg", "jpeg"]


class ChartsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=FILE_FORMAT_CHOICES, default="svg")


class ChartPlotSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], help_text=help_texts.TOPIC_FIELD, required=True
    )
    metric = serializers.ChoiceField(
        choices=[], help_text=help_texts.METRIC_FIELD, required=True
    )

    stratum = serializers.CharField(
        required=False, help_text=help_texts.STRATUM_FIELD, allow_blank=True, default=""
    )
    geography = serializers.CharField(
        required=False,
        help_text=help_texts.GEOGRAPHY_FIELD,
        allow_blank=True,
        default="",
    )
    geography_type = serializers.CharField(
        required=False,
        help_text=help_texts.GEOGRAPHY_TYPE_FIELD,
        allow_blank=True,
        default="",
    )

    chart_type = serializers.ChoiceField(
        choices=ChartTypes.choices(),
        help_text=help_texts.CHART_TYPE_FIELD,
        required=True,
    )
    date_from = serializers.DateField(
        help_text=help_texts.DATE_FROM_FIELD,
        required=False,
        default="",
        allow_null=True,
    )

    def to_models(self):
        return ChartsPlotParameters(**self.data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except RuntimeError:
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


CHARTS_RESPONSE_HELP_TEXT: str = """
The specified chart type (E.g Waffle) in png format
"""


class ChartsResponseSerializer(serializers.Serializer):
    chart = serializers.FileField(help_text=CHARTS_RESPONSE_HELP_TEXT)


class ChartPlotsListSerializer(serializers.ListSerializer):
    child = ChartPlotSerializer()


class ChartsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        help_text=help_texts.CHART_FILE_FORMAT_FIELD,
        default="svg",
    )
    plots = ChartPlotsListSerializer()

    def to_models(self) -> ChartPlots:
        return ChartPlots(
            plots=self.data["plots"],
            file_format=self.data["file_format"],
        )
