from rest_framework import serializers

from public_api.metrics_interface.interface import MetricsPublicAPIInterface


class APIHeadlineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricsPublicAPIInterface.get_api_headline_model()
        fields = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "geography_code",
            "metric",
            "metric_group",
            "stratum",
            "sex",
            "age",
            "year",
            "month",
            "epiweek",
            "date",
            "metric_value",
            "in_reporting_delay_period",
        ]
