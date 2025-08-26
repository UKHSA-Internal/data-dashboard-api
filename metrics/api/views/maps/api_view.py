import logging
import time

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.maps import MapsRequestSerializer
from metrics.interfaces.maps.access import MapOutput, get_maps_output

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
                name="6-in-1 (1 year) 2023 coverage",
                value=REQUEST_PAYLOAD_EXAMPLE,
                request_only=True,
            )
        ],
    )
    @cache_response(is_reserved_namespace=True)
    def post(cls, request: Request) -> Response:
        start_time = time.time()

        serializer = MapsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maps_parameters = serializer.to_models(request=request)
        maps_output: MapOutput = get_maps_output(maps_parameters=maps_parameters)
        response_data = maps_output.output()

        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        logger.info("Fulfilled maps request in: %s seconds", elapsed_time)

        return Response(data=response_data)
