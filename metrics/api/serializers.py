from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import Metric, Topic


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
        choices=Topic.objects.all().values_list("name", flat=True), default="COVID-19"
    )
    metric = serializers.ChoiceField(Metric.objects.all().values_list("name", flat=True), required=True)
    chart_type = serializers.ChoiceField(
        choices=["simple_line_graph", "waffle", "line_with_shaded_section"], required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
