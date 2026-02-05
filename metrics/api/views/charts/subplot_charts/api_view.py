import io
import logging
from http import HTTPStatus

from django.http.response import FileResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.serializers.charts import (
    EncodedChartResponseSerializer,
)
from metrics.api.serializers.charts.subplot_charts import (
    ChartPreviewQueryParamsSerializer,
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

    @extend_schema(
        request=SubplotChartRequestSerializer,
        parameters=[ChartPreviewQueryParamsSerializer],
        examples=[
            OpenApiExample(
                name="MMR1 (2 years)", value=REQUEST_PAYLOAD_EXAMPLE, request_only=True
            )
        ],
    )
    def post(self, request, *args, **kwargs) -> FileResponse | Response:
        chart_preview_serializer = ChartPreviewQueryParamsSerializer(
            data=request.query_params
        )
        chart_preview_serializer.is_valid(raise_exception=True)
        payload = chart_preview_serializer.validated_data

        if payload.get("preview", False):
            return self._process_post_request_as_preview(request, *args, **kwargs)
        return self._process_post_request_as_encoded_svg(request, *args, **kwargs)

    @cache_response(timeout=0)
    def _process_post_request_as_preview(
        self, request, *args, **kwargs
    ) -> FileResponse:
        """Handles the inbound request as `preview=true` in this case we don't use the cache

        Notes:
            - With a timeout of `0`, the response is never
            actually put into the cache

        Returns:
            `Response` containing the JSON data for the
                chart and all of its associated deliverables

        """
        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )
        return self._handle_chart_as_file(
            subplot_chart_parameters=subplot_chart_parameters
        )

    @cache_response()
    def _process_post_request_as_encoded_svg(
        self, request, *args, **kwargs
    ) -> Response:
        """Handles the inbound request as `preview=false` in this case we use the cache

        Returns:
            `FileResponse` containing the chart image

        """
        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )
        return self._handle_encoded_svg(
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

        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        serializer = EncodedChartResponseSerializer(data=chart_result.output())
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data)

    @classmethod
    def _handle_chart_as_file(
        cls, subplot_chart_parameters: SubplotChartRequestParameters
    ) -> FileResponse | Response:
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
