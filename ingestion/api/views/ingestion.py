from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from ingestion.file_ingestion import file_ingester

INGESTION_API_TAG = "ingestion"


class IngestionView(APIView):
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
        tags=[INGESTION_API_TAG],
    )
    def post(self, request, *args, **kwargs):
        """
        This endpoint can be used to upload source data files for ingestion.

        Note that the filename **must contain one the following keywords**:

        - `headline`

        - `cases`

        - `deaths`

        - `healthcare`

        - `testing`

        - `vaccinations`

        """
        file_ingester(file=request.FILES.get("file"))
        return Response(status=HTTPStatus.CREATED.value)
