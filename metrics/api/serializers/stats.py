from rest_framework import serializers

from metrics.data.models.api_models import APITimeSeries


class DashboardSerializer(serializers.ModelSerializer):
    # Meta class only needed for Swagger
    class Meta:
        model = APITimeSeries
        fields = "__all__"
