from typing import List

from django.db.models import Manager
from rest_framework import serializers

from metrics.data.models.core_models import Metric, Topic
from metrics.interfaces.charts.access import ChartTypes

FILE_FORMAT_CHOICES: List[str] = ["svg", "png", "jpg", "jpeg"]


class ChartsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=FILE_FORMAT_CHOICES, default="svg")


DATE_FROM_FIELD_HELP_TEXT: str = """
The date from which to begin analysing data from. 
If nothing is provided, a default of **1 year ago from the current date** will be applied.
"""


class ChartsRequestSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=[], required=True)
    metric = serializers.ChoiceField(choices=[], required=True)
    chart_type = serializers.ChoiceField(choices=ChartTypes.choices(), required=True)
    date_from = serializers.DateField(
        help_text=DATE_FROM_FIELD_HELP_TEXT, required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
