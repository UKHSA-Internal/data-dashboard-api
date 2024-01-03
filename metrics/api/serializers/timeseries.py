from rest_framework import serializers

from metrics.data.models.core_models import CoreTimeSeries


class CoreTimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreTimeSeries
        fields = "__all__"
