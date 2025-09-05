import logging
from http import HTTPStatus

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.views.tables.single_category_tables import TABLES_API_TAG
from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.domain.models import ChartRequestParams
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.plots.access import (
    DataNotFoundForAnyPlotError,
    InvalidPlotParametersError,
)
from metrics.interfaces.tables.subplot_tables import access

logger = logging.getLogger(__name__)


class TablesSubplotView(APIView):
    permission_classes = []

    @classmethod
    @extend_schema(
        request=SubplotChartRequestSerializer,
        examples=[
            OpenApiExample(
                name="MMR1 (2 years)", value=REQUEST_PAYLOAD_EXAMPLE, request_only=True
            )
        ],
        tags=[TABLES_API_TAG],
    )
    @cache_response()
    @require_authorisation
    def post(cls, request, *args, **kwargs):
        serializer = SubplotChartRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subplot_chart_parameters: SubplotChartRequestParameters = serializer.to_models(
            request=request
        )
        request_params_per_group: list[ChartRequestParams] = (
            subplot_chart_parameters.output_payload_for_tables()
        )

        try:
            tabular_data: list[dict] = access.generate_subplot_table(
                request_params_per_group=request_params_per_group
            )
        except (InvalidPlotParametersError, DataNotFoundForAnyPlotError) as error:
            return Response(
                status=HTTPStatus.BAD_REQUEST, data={"error_message": str(error)}
            )

        return Response(tabular_data)
