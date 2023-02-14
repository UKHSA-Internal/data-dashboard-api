from apiv3.models import WeeklyTimeSeries

from rest_framework import serializers


class WeeklyTimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyTimeSeries
        fields = ['parent_theme', 'child_theme', 'topic', 'geography_type', 'geography', 'metric', 'stratum', 'year', 'epiweek', 'start_date', 'metric_value']
