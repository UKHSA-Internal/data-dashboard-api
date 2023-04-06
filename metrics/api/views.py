import os
from http import HTTPStatus

from django.http import FileResponse, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.api.serializers import ChartsQuerySerializer, ChartsRequestSerializer
from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data
from metrics.domain.charts.data_visualization import (
    ChartNotSupportedError,
    generate_corresponding_chart, generate_chart,
)


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        return HttpResponse(HTTPStatus.OK.value)


class ChartView(APIView):
    permission_classes = [HasAPIKey]

    @swagger_auto_schema(query_serializer=ChartsQuerySerializer)
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification

        There are 2 mandatory URL parameters:

        - `topic` - relates to a type of disease

        - `category` - refers to the type of metric (like deaths or cases)

        Currently, the available permutations are:
        | Topic | Category |
        | ----- | -------- |
        | COVID-19 | Vaccinations |
        | COVID-19 | Cases |
        | COVID-19 | Deaths |
        | Influenza | Healthcare |
        | Influenza | Testing |

        Where a given permutation is not available the endpoint will respond with a `HTTP 404 NOT FOUND` error

        There is also an optional query param of `file_format`.
        By default, this will be set to `svg`.
        In addition to `svg` the following options are available:

        - `png`

        - `jpg`

        - `jpeg`

        """
        category: str = kwargs["category"]
        topic: str = kwargs["topic"]

        query_serializer = ChartsQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        file_format = query_serializer.data["file_format"]

        try:
            filename: str = generate_corresponding_chart(
                topic=topic, category=category, file_format=file_format
            )
        except ChartNotSupportedError:
            return Response(status=HTTPStatus.NOT_FOUND)

        return self._return_image(filename=filename)

    @staticmethod
    def _return_image(filename: str) -> FileResponse:
        image = open(filename, "rb")
        response = FileResponse(image)

        os.remove(filename)

        return response


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [HasAPIKey]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="File to be uploaded",
            )
        ],
        deprecated=True,
    )
    def put(self, request, *args, **kwargs):
        """
        Note that this endpoint is **deprecated** and should only be used for demo/testing purposes.
        """
        load_core_data(filename=request.FILES.get("file"))
        generate_api_time_series()
        return Response(status=204)




class ChartsView(APIView):
    @swagger_auto_schema(
        query_serializer=ChartsRequestSerializer)
    def get(self, request, *args, **kwargs):
        """

        """

        query_serializer = ChartsRequestSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        topic = query_serializer.data["topic"]
        metric = query_serializer.data["metric"]
        chart_type = query_serializer.data["chart_type"]
        date_from = query_serializer.data["date_from"]

        try:
            filename: str = generate_chart(topic=topic, metric=metric, chart_type=chart_type, date_from=date_from)
        except ChartNotSupportedError:
            return Response(status=HTTPStatus.NOT_FOUND)

        return self._return_image(filename=filename)

    @staticmethod
    def _return_image(filename: str) -> FileResponse:
        image = open(filename, "rb")
        response = FileResponse(image)

        os.remove(filename)

        return response