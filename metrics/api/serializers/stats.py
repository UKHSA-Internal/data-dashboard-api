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


HEADLINE_METRIC_VALUE_FIELD_HELP_TEXT: str = """
The associated value of the headline metric which was queried for. E.g. `new_cases_7days_change`
"""


class HeadlinesResponseSerializer(serializers.Serializer):
    value = serializers.FloatField(help_text=HEADLINE_METRIC_VALUE_FIELD_HELP_TEXT)
