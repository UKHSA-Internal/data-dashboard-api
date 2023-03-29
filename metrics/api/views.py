from http import HTTPStatus

from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data
from metrics.domain.charts.data_visualization import (
    ChartNotSupportedError,
    generate_corresponding_chart,
)


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        """This endpoint can be used to generate charts conforming to the UK Gov Specification

        Where a `topic` relates to a type of disease, and `category` refers to the type of metric (like deaths or cases).

        Currently, the available permutations are:
        | Topic | Category |
        | ----- | -------- |
        | COVID-19 | Vaccinations |
        | COVID-19 | Cases |
        | COVID-19 | Deaths |
        | Influenza | Healthcare |
        | Influenza | Testing |

        Where a given permutation is not available the endpoint will respond with a `HTTP 404 NOT FOUND` error

        """
        category: str = kwargs["category"]
        topic: str = kwargs["topic"]

        try:
            filename: str = generate_corresponding_chart(topic=topic, category=category)
        except ChartNotSupportedError:
            return Response(status=HTTPStatus.NOT_FOUND)

        image = open(filename, "rb")
        return FileResponse(image)


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

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
