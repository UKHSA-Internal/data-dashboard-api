import logging
from http import HTTPStatus

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

import config
from metrics.api.enums import AppMode
from metrics.api.serializers.charts import (
    ChartsResponseSerializer,
)
from metrics.api.serializers.charts.dual_category_charts import (
    DualCategoryChartSerializer,
)
from metrics.domain.charts.colour_scheme import RGBAChartLineColours

CHARTS_API_TAG = "charts"

logger = logging.getLogger(__name__)


EXAMPLE_DUAL_CATEGORY_CHART_REQUEST_PAYLOAD = {
    "file_format": "svg",
    "chart_height": 200,
    "chart_width": 320,
    "x_axis": "metric",
    "primary_field_values": ["m", "f"],
    "y_axis": "sex",
    "x_axis_title": "",
    "y_axis_title": "",
    "y_axis_minimum_value": None,
    "y_axis_maximum_value": None,
    "chart_type": "bar",
    "secondary_category": "age",
    "static_fields": {
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "metric": "COVID-19_cases_rateRollingMean",
        "stratum": "default",
        "age": "all",
        "geography": "England",
        "geography_type": "Nation",
        "sex": "all",
        "date_from": "2020-02-01",
        "date_to": "2021-02-01",
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

    @classmethod
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
    def post(cls, request, *args, **kwargs):
        request_serializer = DualCategoryChartSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chart_request_params = request_serializer.to_models(request=request)

        logger.info("This endpoint is not yet complete")

        temporary_dict_representation = chart_request_params.model_dump()
        temporary_dict_representation.pop("request")

        return Response(data=temporary_dict_representation)
