from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from metrics.api.serializers import BulkDownloadsSerializer
from metrics.api.views.downloads.common import DOWNLOADS_API_TAG
from metrics.domain.bulk_downloads.get_downloads_archive import (
    get_bulk_downloads_archive,
)


class BulkDownloadsView(APIView):
    @classmethod
    @extend_schema(
        parameters=[BulkDownloadsSerializer],
        tags=[DOWNLOADS_API_TAG],
    )
    def get(cls, request, *args, **kwargs):
        """This endpoint can be used to get all downloads from the current dashboard and return them in a zip file

        Note this endpoint will return a zipfile containing a collection of folders based on page names, each
        folder will contain a series of csv or json files named after the charts currently published on the dashboard.

        # Main errors

        If any of the charts fail to be retrieved a 500 server error will be returned and the file
        will not be downloaded.

        This endpoint supports both csv and json format for its downloads
        this makes the 'file_format' parameter a required field
        not supplying this as a query parameter will result in a 400 Bad Request.

        """
        request_serializer = BulkDownloadsSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        file_format = request_serializer.data["file_format"]

        compressed_downloads = get_bulk_downloads_archive(file_format=file_format)

        response = HttpResponse(
            compressed_downloads["zip_file_data"], content_type="application/zip"
        )
        response["Content-Disposition"] = (
            f"attachment; filename={compressed_downloads['zip_file_name']}"
        )
        return response
