from django.db.models import Manager
from rest_framework import serializers

from metrics.api.serializers import help_texts
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import Metric, Topic


class DashboardSerializer(serializers.ModelSerializer):
    # Meta class only needed for Swagger
    class Meta:
        model = APITimeSeries
        fields = "__all__"


class HeadlinesQuerySerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], required=True, help_text=help_texts.TOPIC_FIELD
    )
    metric = serializers.ChoiceField(
        choices=[],
        required=True,
        help_text=help_texts.METRIC_FIELD.format("new_cases_7days_sum"),
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
