from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data
from metrics.domain.charts.data_visualization import write_chart_file_for_topic


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        """
        This endpoint can be used to generate charts conforming to the UK Gov Design System.
        `topic` relates to the particular disease.

        Currently, the available topics are:

        - `COVID-19`

        - `Influenza`

        - `RSV`

        - `Rhinovirus`

        - `Parainfluenza`

        - `hMPV`

        - `Adenovirus`

        - `Acute Respiratory Infections`

        """
        filename = write_chart_file_for_topic(topic=kwargs["topic"], file_format="svg")

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
        # CoreTimeSeries.objects.all().delete()
        # APITimeSeries.objects.all().delete()

        load_core_data(filename=request.FILES.get("file"))
        generate_api_time_series()
        return Response(status=204)
