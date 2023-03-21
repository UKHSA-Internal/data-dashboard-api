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
            "dt",
            "metric_value",
        ]
