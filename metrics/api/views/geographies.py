from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from caching.private_api.decorators import cache_response
from metrics.api.serializers.geographies import (
    GEOGRAPHY_TYPE_RESULT,
    GeographiesSerializer,
    GeographyTypesDetailSerializer,
    GeographyTypesSerializer,
)
from metrics.data.models.core_models import GeographyType

GEOGRAPHIES_API_TAG = "geographies"


@extend_schema(tags=[GEOGRAPHIES_API_TAG], deprecated=True)
class GeographyTypesViewSet(ReadOnlyModelViewSet):
    """
    Note: This ViewSet and the `geographies/v1` endpoint have been deprecated.
        This will be replaced by a new `API_VIEW` and v2 endpoint that retrieves geographies
        data based on a selected topic.
    """

    permission_classes = []
    queryset = GeographyType.objects.all().order_by("name")
    serializer_class = GeographyTypesSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeographyTypesDetailSerializer
        return self.serializer_class

    @cache_response()
    def list(self, request, *args, **kwargs):  # noqa: A003
        return super().list(request, *args, **kwargs)

    @cache_response()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=[GEOGRAPHIES_API_TAG])
class GeographiesView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs) -> Response:
        payload = {"topic": self.kwargs["topic"]}
        serializer = GeographiesSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        data: list[GEOGRAPHY_TYPE_RESULT] = serializer.data()

        return Response(data)
