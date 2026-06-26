from rest_framework import serializers

from public_api.metrics_interface.interface import MetricsPublicAPIInterface


class APITimeSeriesListSerializerv3(serializers.ModelSerializer):
    class Meta:
        model = MetricsPublicAPIInterface.get_api_timeseries_model()
        fields = [
            "age",
            "date",
            "epiweek",
            "geography",
            "geography_code",
            "geography_type",
            "in_reporting_delay_period",
            "metric",
            "metric_group",
            "metric_value",
            "month",
            "sex",
            "stratum",
            "sub_theme",
            "theme",
            "topic",
            "year",
        ]


class APIHeadlineListSerializerv3(serializers.ModelSerializer):
    class Meta:
        model = MetricsPublicAPIInterface.get_api_headline_model()
        fields = [
            "age",
            "geography",
            "geography_code",
            "geography_type",
            "lower_confidence",
            "metric",
            "metric_group",
            "metric_value",
            "period_end",
            "period_start",
            "sex",
            "stratum",
            "sub_theme",
            "theme",
            "topic",
            "upper_confidence",
        ]
