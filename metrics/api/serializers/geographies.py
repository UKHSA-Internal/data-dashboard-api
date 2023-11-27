from rest_framework import serializers

from metrics.data.models.core_models import Geography, GeographyType


class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = ["id", "name"]


class GeographyTypesDetailSerializer(serializers.ModelSerializer):
    geographies = GeographySerializer(many=True, read_only=True)

    class Meta:
        model = GeographyType
        fields = ["geographies"]


class GeographyTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographyType
        fields = ["id", "name"]
