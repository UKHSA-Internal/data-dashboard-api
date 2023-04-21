from typing import List, Optional

from django.db.models import Manager
from pydantic import BaseModel
from rest_framework import serializers

from metrics.data.models.core_models import (
    Geography,
    GeographyType,
    Metric,
    Stratum,
    Topic,
)
from metrics.interfaces.charts.access import ChartTypes

FILE_FORMAT_CHOICES: List[str] = ["svg", "png", "jpg", "jpeg"]


class ChartsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(choices=FILE_FORMAT_CHOICES, default="svg")


DATE_FROM_FIELD_HELP_TEXT: str = """
The date from which to begin analysing data from. 
If nothing is provided, a default of **1 year ago from the current date** will be applied.
"""


class ChartsRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(required=True)
    metric = serializers.CharField(required=True)

    stratum = serializers.CharField(required=False)
    geography = serializers.CharField(required=False)
    geography_type = serializers.CharField(required=False)

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

    @property
    def stratum_manager(self) -> Manager:
        return self.context.get("stratum_manager", Stratum.objects)

    @property
    def geography_manager(self) -> Manager:
        return self.context.get("geography_manager", Geography.objects)

    @property
    def geography_type_manager(self) -> Manager:
        return self.context.get("geography_type_manager", GeographyType.objects)


class DataPlotModel(BaseModel):
    TOPIC: str
    METRIC: str
    CHART_TYPE: str
    DATE_FROM: Optional[str]
    DATE_TO: Optional[str]
    STRATUM: Optional[str]
    GEOGRAPHY: Optional[str]
    GEOGRAPHY_TYPE: Optional[str]


class ChartsListRequestSerializer(serializers.ListSerializer):
    child = ChartsRequestSerializer()

    def to_models(self) -> DataPlotModel:

        for child in self.child:
            print(child)

