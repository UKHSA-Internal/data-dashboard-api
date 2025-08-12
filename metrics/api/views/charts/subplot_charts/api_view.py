import io
import logging
from http import HTTPStatus

from django.http.response import FileResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.charts import (
    EncodedChartResponseSerializer,
)
from metrics.api.serializers.charts.subplot_charts import (
    ChartQueryParamsSerializer,
    SubplotChartRequestSerializer,
)
from metrics.api.views.charts.subplot_charts.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.charts.common.generation import ChartResult
from metrics.interfaces.charts.subplot_charts import access
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)

SUBPLOT_CHARTS_API_TAG = "charts"

logger = logging.getLogger(__name__)


@extend_schema(tags=[SUBPLOT_CHARTS_API_TAG])
class SubplotChartsView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=SubplotChartRequestSerializer,
        parameters=[ChartQueryParamsSerializer],
        examples=[
            OpenApiExample(
                name="MMR1 (2 years)", value=REQUEST_PAYLOAD_EXAMPLE, request_only=True
            )
        ],
    )
    def post(cls, request):
        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )

        chart_preview_serializer = ChartQueryParamsSerializer(data=request.query_params)
        chart_preview_serializer.is_valid(raise_exception=True)
        payload = chart_preview_serializer.validated_data

        if payload["preview"]:
            return cls._handle_chart_as_file(
                subplot_chart_parameters=subplot_chart_parameters
            )
        return cls._handle_encoded_svg(
            subplot_chart_parameters=subplot_chart_parameters
        )

    @classmethod
    def _handle_encoded_svg(
        cls, subplot_chart_parameters: SubplotChartRequestParameters
    ) -> Response:
        try:
            chart_result: ChartResult = access.generate_encoded_sub_plot_chart_figure(
                chart_request_params=subplot_chart_parameters,
            )

            serializer = EncodedChartResponseSerializer(data=chart_result.output())
            serializer.is_valid(raise_exception=True)

        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(data=serializer.data)

    @classmethod
    def _handle_chart_as_file(
        cls, subplot_chart_parameters: SubplotChartRequestParameters
    ) -> Response:
        try:
            chart_result: bytes = access.generate_sub_plot_chart_image(
                chart_request_params=subplot_chart_parameters,
            )

        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return FileResponse(
            io.BytesIO(chart_result),
            content_type=f"image/{subplot_chart_parameters.file_format}",
        )
