from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.maps import MapsRequestSerializer

MAPS_API_TAG = "maps"


@extend_schema(tags=[MAPS_API_TAG])
class MapsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(responses=MapsRequestSerializer, parameters=[MapsRequestSerializer])
    def post(cls, request):
        return Response()
