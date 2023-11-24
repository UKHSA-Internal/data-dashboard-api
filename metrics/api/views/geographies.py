from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ReadOnlyModelViewSet

from metrics.api.serializers.geographies import (
    GeographyTypesDetailSerializer,
    GeographyTypesSerializer,
)
from metrics.data.models.core_models import GeographyType

GEOGRAPHIES_API_TAG = "geographies"


@extend_schema(tags=[GEOGRAPHIES_API_TAG])
class GeographyTypesViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    queryset = GeographyType.objects.all().order_by("name")
    serializer_class = GeographyTypesSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeographyTypesDetailSerializer
        return self.serializer_class
