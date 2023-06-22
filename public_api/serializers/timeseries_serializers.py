from rest_framework import serializers

from public_api.metrics_interface.interface import MetricsPublicAPIInterface


class APITimeSeriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricsPublicAPIInterface.get_api_timeseries_model()
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
