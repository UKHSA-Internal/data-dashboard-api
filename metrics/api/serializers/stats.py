from django.db.models import Manager
from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import Metric, Topic


class DashboardSerializer(serializers.ModelSerializer):
    # Meta class only needed for Swagger
    class Meta:
        model = APITimeSeries
        fields = "__all__"


TOPIC_FIELD_HELP_TEXT: str = "The name of the topic being queried for. E.g. `COVID-19`"
TREND_METRIC_NAME_FIELD_HELP_TEXT: str = """
The name of the main change type metric being queried for. E.g. `new_cases_7days_change`
"""
TREND_PERCENTAGE_METRIC_NAME_FIELD_HELP_TEXT: str = """
The name of the percentage change type metric being queried for. E.g. `new_cases_7days_change_percentage`
"""


class HeadlinesQuerySerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], required=True, help_text=TOPIC_FIELD_HELP_TEXT
    )
    metric = serializers.ChoiceField(
        choices=[], required=True, help_text=TREND_METRIC_NAME_FIELD_HELP_TEXT
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


TREND_METRIC_VALUE_FIELD_HELP_TEXT: str = """
The associated value of the main change type metric which was queried for. E.g. `10`
"""
TREND_PERCENTAGE_METRIC_VALUE_FIELD_HELP_TEXT: str = """
The associated value of the percentage change type metric being queried for. E.g. `3.2` would be considered as +3.2%
"""


class TrendsQuerySerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], required=True, help_text=TOPIC_FIELD_HELP_TEXT
    )
    metric = serializers.ChoiceField(
        choices=[], required=True, help_text=TREND_METRIC_NAME_FIELD_HELP_TEXT
    )
    percentage_metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=TREND_PERCENTAGE_METRIC_NAME_FIELD_HELP_TEXT,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate_field_choices()

    def _populate_field_choices(self) -> None:
        self.fields["topic"].choices = self.topic_manager.get_all_names()
        self.fields[
            "metric"
        ].choices = self.metric_manager.get_all_unique_change_type_names()
        self.fields[
            "percentage_metric"
        ].choices = self.metric_manager.get_all_unique_percent_change_type_names()

    @property
    def topic_manager(self) -> Manager:
        return self.context.get("topic_manager", Topic.objects)

    @property
    def metric_manager(self) -> Manager:
        return self.context.get("metric_manager", Metric.objects)


DIRECTION_FIELD_HELP_TEXT: str = """
The direction in which the trend is represented as. 
This can be one of the following `up`, `neutral` or `down`.
"""

COLOUR_FIELD_HELP_TEXT: str = """
The colour in which the trend is represented as. 
This can be one of the following `green`, `neutral` or `red`.
"""


class TrendsResponseSerializer(serializers.Serializer):
    metric = serializers.CharField(help_text=TREND_METRIC_NAME_FIELD_HELP_TEXT)
    metric_value = serializers.FloatField(help_text=TREND_METRIC_VALUE_FIELD_HELP_TEXT)

    percentage_metric = serializers.CharField(
        help_text=TREND_PERCENTAGE_METRIC_NAME_FIELD_HELP_TEXT
    )
    percentage_metric_value = serializers.FloatField(
        help_text=TREND_METRIC_VALUE_FIELD_HELP_TEXT
    )

    direction = serializers.CharField(help_text=DIRECTION_FIELD_HELP_TEXT)
    colour = serializers.CharField(help_text=COLOUR_FIELD_HELP_TEXT)
