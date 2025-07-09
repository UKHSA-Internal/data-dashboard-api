from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.geographies import (
    GEOGRAPHY_TYPE_RESULT,
    GeographiesForGeographyTypeSerializer,
    GeographiesForTopicSerializer,
    GeographiesRequestSerializer,
    GeographiesRequestSerializerDeprecated,
    GeographiesResponseSerializer,
)

GEOGRAPHIES_API_TAG = "geographies"


@extend_schema(
    tags=[GEOGRAPHIES_API_TAG],
)
class GeographiesViewDeprecated(APIView):
    permission_classes = []

    @cache_response()
    @extend_schema(
        request=GeographiesRequestSerializerDeprecated,
        responses={HTTPStatus.OK.value: GeographiesResponseSerializer},
        deprecated=True,
    )
    def get(self, request, *args, **kwargs) -> Response:
        """This endpoint returns a list of geography types based on a `Topic` name along with an aggregated
        list of their geographies.

        ---

        # Main errors

        This endpoint requires a valid topic name to be provided and will return a `Bad Request` 400
        if one is not provided.

        """
        payload = {"topic": self.kwargs["topic"]}
        serializer = GeographiesForTopicSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        data: list[GEOGRAPHY_TYPE_RESULT] = serializer.data()

        return Response(data)


@extend_schema(
    tags=[GEOGRAPHIES_API_TAG],
)
class GeographiesView(APIView):
    permission_classes = []

    @cache_response()
    @extend_schema(
        request=GeographiesRequestSerializer,
        parameters=[GeographiesRequestSerializer],
        responses={HTTPStatus.OK.value: GeographiesResponseSerializer},
    )
    def get(self, request, *args, **kwargs) -> Response:
        """This endpoint returns a list of geography types along with an aggregated list of their geographies.

        ---

        # Main errors

        A query parameter of either `topic` or `geography_type` must be provided.
        If neither are provided **or** both are provided, then a 400 `Bad Request` 400 will be returned.

        """
        request_serializer = GeographiesRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        payload = request_serializer.data

        if "topic" in payload:
            data: list[GEOGRAPHY_TYPE_RESULT] = self._handle_geographies_by_topic(
                payload=payload
            )
        else:
            data: list[GEOGRAPHY_TYPE_RESULT] = (
                self._handle_geographies_by_geography_type(payload=payload)
            )

        return Response(data)

    @classmethod
    def _handle_geographies_by_topic(
        cls, *, payload: dict
    ) -> list[GEOGRAPHY_TYPE_RESULT]:
        serializer = GeographiesForTopicSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return serializer.data()

    @classmethod
    def _handle_geographies_by_geography_type(
        cls, *, payload: dict
    ) -> list[GEOGRAPHY_TYPE_RESULT]:
        serializer = GeographiesForGeographyTypeSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return serializer.data()
