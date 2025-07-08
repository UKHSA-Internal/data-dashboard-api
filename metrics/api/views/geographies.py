from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.geographies import (
    GEOGRAPHY_TYPE_RESULT,
    GeographiesRequestSerializer,
    GeographiesResponseSerializer,
    GeographiesSerializer,
)

GEOGRAPHIES_API_TAG = "geographies"


@extend_schema(
    tags=[GEOGRAPHIES_API_TAG],
)
class GeographiesViewDeprecated(APIView):
    permission_classes = []

    @cache_response()
    @extend_schema(
        request=GeographiesRequestSerializer,
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
        serializer = GeographiesSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        data: list[GEOGRAPHY_TYPE_RESULT] = serializer.data()

        return Response(data)
