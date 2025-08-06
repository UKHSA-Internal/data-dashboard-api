import io
import logging

from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.charts.subplot_charts import access

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

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )

        # Temporary response for testing subplot `ChartInterface`
        # follow on ticket will include exception handling and encoded charts
        chart_image: bytes = access.generate_chart_file(
            chart_request_params=subplot_chart_parameters,
        )

        return FileResponse(
            io.BytesIO(chart_image),
            content_type="image/svg",
        )
