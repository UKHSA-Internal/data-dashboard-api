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
    theme = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sub_theme = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    topic = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    metric = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    stratum = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    age = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    geography_type = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    geography = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class MapAccompanyingPointSerializer(serializers.Serializer):
    label_prefix = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    label_suffix = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    parameters = OptionalParametersSerializer(required=False)


class MapAccompanyingPointsSerializer(serializers.ListSerializer):
    child = MapAccompanyingPointSerializer()


ACCOMPANYING_POINT_PAYLOAD_TYPE = dict[str, str | dict[str, str]]
MAIN_PARAMETERS_PAYLOAD_TYPE = dict[str, str | list[str]]


class MapsRequestSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)

    parameters = MapMainParametersSerializer(required=True)
    accompanying_points = MapAccompanyingPointsSerializer(required=False)

    def to_models(self, request: Request) -> MapsParameters:
        accompanying_points: list[ACCOMPANYING_POINT_PAYLOAD_TYPE] = (
            self.validated_data.pop("accompanying_points")
        )
        main_parameters: MAIN_PARAMETERS_PAYLOAD_TYPE = self.validated_data[
            "parameters"
        ]

        for accompanying_point in accompanying_points:
            accompanying_point["parameters"].update(
                {
                    key: value
                    for key, value in main_parameters.items()
                    if key not in accompanying_point["parameters"]
                }
            )

        return MapsParameters(
            **self.validated_data,
            accompanying_points=accompanying_points,
            request=request
        )
