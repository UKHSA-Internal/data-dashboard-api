from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from caching.private_api.decorators import cache_response
from metrics.api.decorators.auth import require_authorisation
from metrics.api.serializers.charts.subplot_charts import SubplotChartRequestSerializer
from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.api.views.tables.single_category_tables import TABLES_API_TAG, logger
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters


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

        logger.info(
            "Subplot chart parameters: %s", subplot_chart_parameters.model_dump()
        )
        logger.info("This endpoint is incomplete, returning fake data")

        tabular_data = [
            {
                "reference": "England",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "87.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "82.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "84.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": "86.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "83.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": "90.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "East Midlands",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "85.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "87.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "90.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": "89.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "91.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": "88.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "86.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": "92.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "Nottingham",
                "values": [
                    {
                        "label": "6-in-1 (12 months)",
                        "value": "72.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Rota (12 months)",
                        "value": "69.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB (12 months)",
                        "value": "67.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "6-in-1 (24 months)",
                        "value": "68.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "PCV booster (24 months)",
                        "value": "73.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MMR1 (24 months)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Hib/MenC (24 months)",
                        "value": "74.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "MenB booster (24 months)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "5-in-1 (5 years)",
                        "value": "66.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "4-in-1 (5 years)",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]

        return Response(tabular_data)
