from rest_framework import serializers


class APISerializerv3(serializers.ModelSerializer):
    class Meta:
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
            "metric_value",
        ]
