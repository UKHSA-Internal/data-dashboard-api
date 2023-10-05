from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries


class APITimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = APITimeSeries
        fields = [
            "metric_frequency",
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "year",
            "epiweek",
            "date",
            "metric_value",
        ]
