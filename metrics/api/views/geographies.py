from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.geographies import (
    GEOGRAPHY_TYPE_RESULT,
    GeographiesSerializer,
)

GEOGRAPHIES_API_TAG = "geographies"


@extend_schema(tags=[GEOGRAPHIES_API_TAG])
class GeographiesView(APIView):
    permission_classes = []

    @cache_response()
    def get(self, request, *args, **kwargs) -> Response:
        payload = {"topic": self.kwargs["topic"]}
        serializer = GeographiesSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        data: list[GEOGRAPHY_TYPE_RESULT] = serializer.data()

        return Response(data)
