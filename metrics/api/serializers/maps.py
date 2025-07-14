from rest_framework import serializers
from rest_framework.request import Request

from metrics.domain.models.map import MapsParameters


class MapMainParametersSerializer(serializers.Serializer):
    theme = serializers.CharField(required=True)
    sub_theme = serializers.CharField(required=True)
    topic = serializers.CharField(required=True)
    metric = serializers.CharField(required=True)
    stratum = serializers.CharField(required=True)
    age = serializers.CharField(required=True)
    sex = serializers.CharField(required=True)
    geography_type = serializers.CharField(required=True)
    geographies = serializers.ListField(required=True)


class OptionalParametersSerializer(serializers.Serializer):
    theme = serializers.CharField(required=False)
    sub_theme = serializers.CharField(required=False)
    topic = serializers.CharField(required=False)
    metric = serializers.CharField(required=False)
    stratum = serializers.CharField(required=False)
    age = serializers.CharField(required=False)
    sex = serializers.CharField(required=False)
    geography_type = serializers.CharField(required=False)
    geography = serializers.CharField(required=False)


class MapAccompanyingPointSerializer(serializers.Serializer):
    label_prefix = serializers.CharField(required=True)
    label_suffix = serializers.CharField(required=False)
    parameters = OptionalParametersSerializer(required=True)


class MapAccompanyingPointsSerializer(serializers.ListSerializer):
    child = MapAccompanyingPointSerializer()


class MapsRequestSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)

    parameters = MapMainParametersSerializer(required=True)
    accompanying_points = MapAccompanyingPointsSerializer(required=False)

    def to_models(self, request: Request) -> MapsParameters:
        return MapsParameters(**self.validated_data, request=request)
