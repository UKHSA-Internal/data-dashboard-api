from django.db.models import Manager
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.core_models import Metric, Topic


class TrendsQuerySerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], required=True, help_text=help_texts.TOPIC_FIELD
    )
    metric = serializers.ChoiceField(
        choices=[], required=True, help_text=help_texts.TREND_METRIC_NAME_FIELD
    )
    percentage_metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.TREND_PERCENTAGE_METRIC_NAME_FIELD,
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


class TrendsResponseSerializer(serializers.Serializer):
    metric = serializers.CharField(help_text=help_texts.TREND_METRIC_NAME_FIELD)
    metric_value = serializers.FloatField(help_text=help_texts.TREND_METRIC_VALUE_FIELD)

    percentage_metric = serializers.CharField(
        help_text=help_texts.TREND_PERCENTAGE_METRIC_NAME_FIELD
    )
    percentage_metric_value = serializers.FloatField(
        help_text=help_texts.TREND_METRIC_VALUE_FIELD
    )

    direction = serializers.CharField(help_text=help_texts.DIRECTION_FIELD)
    colour = serializers.CharField(help_text=help_texts.COLOUR_FIELD)
