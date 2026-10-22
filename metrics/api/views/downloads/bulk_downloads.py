from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.permissions import PermissionSetsType
from metrics.api.serializers import BulkDownloadsSerializer
from metrics.api.settings import auth
from metrics.api.views.downloads.common import DOWNLOADS_API_TAG
from metrics.domain.bulk_downloads.get_downloads_archive import (
    get_bulk_downloads_archive,
)


def get_permission_sets_for_request(*, request: Request) -> PermissionSetsType | None:
    """Returns the permission sets associated with the given `request`

    Args:
        request: The request made to the endpoint

    Returns:
        The permission sets of the authenticated end user.
        Otherwise, None is returned when authentication is disabled
        or the request was made by an anonymous/unauthenticated user

    """
    if not auth.AUTH_ENABLED or request.auth is None:
        return None

    return getattr(request.user, "permission_sets", None)


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

        Note that downloads are only returned for pages which the end user
        is permitted to view. Unauthenticated requests will only receive
        downloads associated with public pages.

        """
        request_serializer = BulkDownloadsSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        file_format = request_serializer.data["file_format"]
        permission_sets = get_permission_sets_for_request(request=request)

        compressed_downloads = get_bulk_downloads_archive(
            file_format=file_format, permission_sets=permission_sets
        )

        response = HttpResponse(
            compressed_downloads["zip_file_data"], content_type="application/zip"
        )
        response["Content-Disposition"] = (
            f"attachment; filename={compressed_downloads['zip_file_name']}"
        )
        return response
