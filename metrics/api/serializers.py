from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries


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
