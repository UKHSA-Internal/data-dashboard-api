import logging

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer

SUBPLOT_CHARTS_API_TAG = "charts"

logger = logging.getLogger(__name__)


@extend_schema(tags=[SUBPLOT_CHARTS_API_TAG])
class SubplotChartsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(request=[SubplotChartRequestSerializer])
    def post(cls, request):

        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters = serializer.to_models(request=request)

        # Temporary response until interface is completed.
        output = subplot_chart_parameters.model_dump(mode="python", exclude_none=True)
        output.pop("request")

        logger.info("This endpoint is under development")

        return Response(data=output)
