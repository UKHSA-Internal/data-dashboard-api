from django.http.request import HttpRequest
from rest_framework.request import Request

from metrics.api.serializers.maps import MapsRequestSerializer
from metrics.api.views.maps.request_example import REQUEST_PAYLOAD_EXAMPLE
from metrics.domain.models.map import MapsParameters


class TestMapsRequestSerializer:
    def test_to_models_serializes_main_parameters_correctly(self):
        """
        Given a valid payload
        When `to_models()` is called
            from an instance of the `MapsRequestSerializer`
        Then the returned `MapsParameters` holds the correct main parameters
        """
        # Given
        payload = REQUEST_PAYLOAD_EXAMPLE
        fake_request = Request(request=HttpRequest())
        serializer = MapsRequestSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        maps_parameters: MapsParameters = serializer.to_models(request=fake_request)

        # Then
        assert maps_parameters.date_from.strftime("%Y-%m-%d") == payload["date_from"]
        assert maps_parameters.date_to.strftime("%Y-%m-%d") == payload["date_to"]
        assert maps_parameters.parameters.theme == payload["parameters"]["theme"]
        assert (
            maps_parameters.parameters.sub_theme == payload["parameters"]["sub_theme"]
        )
        assert maps_parameters.parameters.topic == payload["parameters"]["topic"]
        assert maps_parameters.parameters.metric == payload["parameters"]["metric"]
        assert maps_parameters.parameters.stratum == payload["parameters"]["stratum"]
        assert maps_parameters.parameters.age == payload["parameters"]["age"]
        assert maps_parameters.parameters.sex == payload["parameters"]["sex"]
        assert (
            maps_parameters.parameters.geography_type
            == payload["parameters"]["geography_type"]
        )
        assert (
            maps_parameters.parameters.geographies
            == payload["parameters"]["geographies"]
        )

    def test_to_models_serializes_first_accompanying_point_correctly(self):
        """
        Given a valid payload
        When `to_models()` is called
            from an instance of the `MapsRequestSerializer`
        Then the returned `MapsParameters` holds
            the correct parameters for the 1st accompanying point
        """
        # Given
        payload = REQUEST_PAYLOAD_EXAMPLE
        fake_request = Request(request=HttpRequest())
        serializer = MapsRequestSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        maps_parameters: MapsParameters = serializer.to_models(request=fake_request)

        # Then
        serialized_accompanying_point = maps_parameters.accompanying_points[0]
        # The fields have been copied successfully from the main parameters
        # to fill the 'gaps' in the accompanying point data
        assert (
            serialized_accompanying_point.parameters.theme
            == payload["parameters"]["theme"]
        )
        assert (
            serialized_accompanying_point.parameters.sub_theme
            == payload["parameters"]["sub_theme"]
        )
        assert (
            serialized_accompanying_point.parameters.topic
            == payload["parameters"]["topic"]
        )
        assert (
            serialized_accompanying_point.parameters.metric
            == payload["parameters"]["metric"]
        )
        assert (
            serialized_accompanying_point.parameters.stratum
            == payload["parameters"]["stratum"]
        )
        assert (
            serialized_accompanying_point.parameters.age == payload["parameters"]["age"]
        )
        assert (
            serialized_accompanying_point.parameters.sex == payload["parameters"]["sex"]
        )
        assert (
            serialized_accompanying_point.parameters.geography_type
            == payload["accompanying_points"][0]["parameters"]["geography_type"]
        )
        assert serialized_accompanying_point.parameters.geography is None

    def test_to_models_serializes_second_accompanying_point_correctly(self):
        """
        Given a valid payload
        When `to_models()` is called
            from an instance of the `MapsRequestSerializer`
        Then the returned `MapsParameters` holds
            the correct parameters for the 2nd accompanying point
        """
        # Given
        payload = REQUEST_PAYLOAD_EXAMPLE
        fake_request = Request(request=HttpRequest())
        serializer = MapsRequestSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        maps_parameters: MapsParameters = serializer.to_models(request=fake_request)

        # Then
        serialized_accompanying_point = maps_parameters.accompanying_points[1]
        # The fields have been copied successfully from the main parameters
        # to fill the 'gaps' in the accompanying point data
        assert (
            serialized_accompanying_point.parameters.theme
            == payload["parameters"]["theme"]
        )
        assert (
            serialized_accompanying_point.parameters.sub_theme
            == payload["parameters"]["sub_theme"]
        )
        assert (
            serialized_accompanying_point.parameters.topic
            == payload["parameters"]["topic"]
        )
        assert (
            serialized_accompanying_point.parameters.metric
            == payload["parameters"]["metric"]
        )
        assert (
            serialized_accompanying_point.parameters.stratum
            == payload["parameters"]["stratum"]
        )
        assert (
            serialized_accompanying_point.parameters.age == payload["parameters"]["age"]
        )
        assert (
            serialized_accompanying_point.parameters.sex == payload["parameters"]["sex"]
        )
        assert (
            serialized_accompanying_point.parameters.geography_type
            == payload["accompanying_points"][1]["parameters"]["geography_type"]
        )
        assert serialized_accompanying_point.parameters.geography is None
