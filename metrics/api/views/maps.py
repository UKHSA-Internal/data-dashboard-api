import logging

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.maps import MapsRequestSerializer
from metrics.interfaces.maps.access import get_maps_data

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
                value={
                    "date_from": "2023-10-30",
                    "date_to": "2023-10-31",
                    "parameters": {
                        "theme": "infectious_disease",
                        "sub_theme": "respiratory",
                        "topic": "COVID-19",
                        "metric": "COVID-19_deaths_ONSByWeek",
                        "stratum": "default",
                        "age": "all",
                        "sex": "all",
                        "geography_type": "Lower Tier Local Authority",
                        "geographies": [],
                    },
                    "accompanying_points": [
                        {
                            "label_prefix": "Some constant",
                            "label_suffix": "",
                            "parameters": {
                                "metric": "COVID-19_cases_rateRollingMean",
                                "geography_type": "Nation",
                                "geography": "England",
                            },
                        }
                    ],
                },
                request_only=True,
            )
        ],
    )
    def post(cls, request):

        serializer = MapsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maps_parameters = serializer.to_models(request=request)
        maps_data = get_maps_data(maps_parameters=maps_parameters)

        logger.info("This endpoint is incomplete")

        return Response(data=maps_data)
