from typing import List

from django.db.models import Manager
from rest_framework import serializers

from metrics.data.models.core_models import (
    Geography,
    GeographyType,
    Metric,
    Stratum,
    Topic,
)
from metrics.domain.models import ChartPlots, ChartsPlotParameters
from metrics.domain.utils import ChartTypes

FILE_FORMAT_CHOICES: List[str] = ["svg", "png", "jpg", "jpeg"]


class ChartsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=FILE_FORMAT_CHOICES, default="svg")


DATE_FROM_FIELD_HELP_TEXT: str = """
The date from which to begin analysing data from. 
If nothing is provided, a default of **1 year ago from the current date** will be applied.
"""


class ChartPlotSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=[], required=True)
    metric = serializers.ChoiceField(choices=[], required=True)

    stratum = serializers.CharField(required=False, default="")
    geography = serializers.CharField(required=False, default="")
    geography_type = serializers.CharField(required=False, default="")

    chart_type = serializers.ChoiceField(choices=ChartTypes.choices(), required=True)
    date_from = serializers.DateField(
        help_text=DATE_FROM_FIELD_HELP_TEXT, required=False, default="",
    )

    def to_models(self):
        return ChartsPlotParameters(**self.data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.populate_choices()
        except RuntimeError:
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

    @property
    def stratum_manager(self) -> Manager:
        return self.context.get("stratum_manager", Stratum.objects)

    @property
    def geography_manager(self) -> Manager:
        return self.context.get("geography_manager", Geography.objects)

    @property
    def geography_type_manager(self) -> Manager:
        return self.context.get("geography_type_manager", GeographyType.objects)


class ChartPlotsListSerializer(serializers.ListSerializer):
    child = ChartPlotSerializer()


class ChartsSerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=FILE_FORMAT_CHOICES, default="png")
    plots = ChartPlotsListSerializer()

    def to_models(self) -> ChartPlots:
        return ChartPlots(
            plots=self.data["plots"],
            file_format=self.data["file_format"],
        )
