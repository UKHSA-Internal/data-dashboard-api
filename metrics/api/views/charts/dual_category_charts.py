import datetime
import io
import logging
from http import HTTPStatus

from django.http import FileResponse
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

import config
from caching.private_api.decorators import cache_response
from metrics.api.enums import AppMode
from metrics.api.serializers.charts import (
    ChartsResponseSerializer,
)
from metrics.api.serializers.charts.common import (
    ChartPreviewQueryParamsSerializer,
    EncodedChartResponseSerializer,
)
from metrics.api.serializers.charts.dual_category_charts import (
    DualCategoryChartSerializer,
)
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.models.charts.dual_category_charts import (
    DualCategoryChartRequestParams,
)
from metrics.interfaces.charts.common.generation import (
    ChartResult,
    generate_chart_as_file,
    generate_encoded_chart,
)
from metrics.interfaces.charts.dual_category_charts.access import (
    DualCategoryChartsInterface,
)
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)

CHARTS_API_TAG = "charts"

logger = logging.getLogger(__name__)

EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD = {
    "file_format": "svg",
    "chart_height": 200,
    "chart_width": 320,
    "x_axis": "date",
    "y_axis": "metric",
    "x_axis_title": "",
    "y_axis_title": "",
    "y_axis_minimum_value": None,
    "y_axis_maximum_value": None,
    "chart_type": "stacked_bar",
    "secondary_category": "age",
    "static_fields": {
        "topic": "COVID-19",
        "metric": "COVID-19_cases_rateRollingMean",
        "stratum": "default",
        "age": "all",
        "geography": "England",
        "geography_type": "Nation",
        "sex": "all",
        "date_from": (datetime.date.today() - datetime.timedelta(days=365)).isoformat(),
        "date_to": datetime.date.today().isoformat(),
    },
    "segments": [
        {
            "secondary_field_value": "00-04",
            "colour": RGBAChartLineColours.COLOUR_1_DARK_BLUE.name,
            "label": "0 to 4 years",
        },
        {
            "secondary_field_value": "05-11",
            "colour": RGBAChartLineColours.COLOUR_3_DARK_PINK.name,
            "label": "5 to 11 years",
        },
    ],
}


class DualCategoryChartsView(APIView):
    permission_classes = []

    def get_permissions(self) -> list[type[permissions.BasePermission]]:
        if AppMode.CMS_ADMIN.value == config.APP_MODE:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        request=DualCategoryChartSerializer,
        responses={HTTPStatus.OK.value: ChartsResponseSerializer},
        tags=[CHARTS_API_TAG],
        examples=[
            OpenApiExample(
                name="COVID-19 age-sex example",
                value=EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD,
                request_only=True,
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
            `Response` containing the rendered chart as an image file

        """
        serializer = DualCategoryChartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chart_request_params: DualCategoryChartRequestParams = serializer.to_models(
            request=request
        )

        return self._handle_chart_as_file(chart_request_params=chart_request_params)

    @classmethod
    def _handle_chart_as_file(
        cls, chart_request_params: DualCategoryChartRequestParams
    ) -> FileResponse | Response:
        """
        Handles the process of generating a chart and returning it as a file response.

        Args:
            chart_request_params: A `DualCategoryChartRequestParams` model containing all the necessary parameters to generate the chart.

        Returns:
            A `FileResponse` containing the generated chart image, or a `Response` with an error message if chart generation fails due to invalid parameters or missing data.
        """
        try:
            chart_image: bytes = generate_chart_as_file(
                chart_request_params=chart_request_params,
                interface=DualCategoryChartsInterface,
            )
        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return FileResponse(
            io.BytesIO(chart_image),
            content_type=f"image/{chart_request_params.file_format}",
        )

    @classmethod
    def _handle_encoded_svg(
        cls, chart_request_params: DualCategoryChartRequestParams
    ) -> Response:
        """Handles the process of generating a chart, encoding it, and returning it in the response.

        Args:
            chart_request_params: A `DualCategoryChartRequestParams` model containing all the necessary parameters to generate the chart.

        Returns:
            A `Response` containing the encoded chart and related metadata, or an error message if chart generation fails due to invalid parameters or missing data.
        """
        try:
            chart_result: ChartResult = generate_encoded_chart(
                chart_request_params=chart_request_params,
                interface=DualCategoryChartsInterface,
            )

        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        serializer = EncodedChartResponseSerializer(data=chart_result.output())
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data)

    @cache_response()
    def _process_post_request_as_encoded_svg(
        self, request, *args, **kwargs
    ) -> Response:
        """Handles the inbound request as `preview=false` in this case we use the cache

        Returns:
            `FileResponse` containing the chart image
        """
        serializer = DualCategoryChartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chart_request_params: DualCategoryChartRequestParams = serializer.to_models(
            request=request
        )
        return self._handle_encoded_svg(chart_request_params=chart_request_params)
