from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

MAPS_API_TAG = "maps"


@extend_schema(
    tags=[MAPS_API_TAG],
)
class MapsView(APIView):
    permission_classes = []

    def post(self, request):
        return Response()
