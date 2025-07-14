import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.maps import MapsRequestSerializer
from metrics.interfaces.maps.access import get_maps_output

from .request_example import REQUEST_PAYLOAD_EXAMPLE

MAPS_API_TAG = "maps"

logger = logging.getLogger(__name__)


@extend_schema(tags=[MAPS_API_TAG])
class MapsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=MapsRequestSerializer,
        examples=[
            OpenApiExample(
                "COVID-19 weekly deaths example",
                value=REQUEST_PAYLOAD_EXAMPLE,
                request_only=True,
            )
        ],
    )
    def post(cls, request):
        serializer = MapsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maps_parameters = serializer.to_models(request=request)
        maps_output = get_maps_output(maps_parameters=maps_parameters)

        logger.info("This endpoint is incomplete")

        return Response(data=maps_output.output())
