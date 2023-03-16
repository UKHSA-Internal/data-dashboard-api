from rest_framework import serializers

from metrics.api.models.api_models import WeeklyTimeSeries


class WeeklyTimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyTimeSeries
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "stratum",
            "year",
            "epiweek",
            "start_date",
            "metric_value",
        ]
