import logging

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.maps import MapsRequestSerializer

MAPS_API_TAG = "maps"

logger = logging.getLogger(__name__)


@extend_schema(tags=[MAPS_API_TAG])
class MapsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(request=MapsRequestSerializer)
    def post(cls, request):

        serializer = MapsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maps_parameters = serializer.to_models(request=request)

        # Temporary block to return serialized request
        # whilst interface is being built
        output = maps_parameters.model_dump(mode="python")
        output.pop("request")

        logger.info("This endpoint is incomplete")

        return Response(data=output)
