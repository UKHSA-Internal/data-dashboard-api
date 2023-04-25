from http import HTTPStatus

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from metrics.data.operations.api_models import generate_api_time_series
from metrics.data.operations.core_models import load_core_data


class HealthView(APIView):
    permission_classes = []

    @staticmethod
    def get(*args, **kwargs):
        return HttpResponse(HTTPStatus.OK.value)


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [HasAPIKey]

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
        deprecated=True,
    )
    def put(self, request, *args, **kwargs):
        """
        Note that this endpoint is **deprecated** and should only be used for demo/testing purposes.
        """
        load_core_data(filename=request.FILES.get("file"))
        generate_api_time_series()
        return Response(status=204)
