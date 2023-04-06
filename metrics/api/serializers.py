from django.db.models import Manager
from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import Metric, Topic
from metrics.interfaces.charts.access import ChartTypes


class APITimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = APITimeSeries
        fields = [
            "period",
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "stratum",
            "sex",
            "year",
            "epiweek",
            "dt",
            "metric_value",
        ]


class DashboardSerializer(serializers.ModelSerializer):
    # Meta class only needed for Swagger
    class Meta:
        model = APITimeSeries
        fields = "__all__"


class ChartsQuerySerializer(serializers.Serializer):
    file_format = serializers.ChoiceField(
        choices=["svg", "png", "jpg", "jpeg"], default="svg"
    )


class ChartsRequestSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(
        choices=[], required=True
    )
    metric = serializers.ChoiceField(
        choices=[], required=True
    )
    chart_type = serializers.ChoiceField(choices=ChartTypes.choices(), required=True)
    date_from = serializers.DateField(required=True)

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
