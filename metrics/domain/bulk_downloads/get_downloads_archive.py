import datetime

from caching.private_api.handlers import get_all_downloads
from common.auth.permissions import PermissionSetsType
from metrics.domain.exports.zip import write_data_to_zip


def generate_zip_filename() -> str:
    """Generates a filename with today's date.

    Returns:
        A string with the downloads file name suffixed with today's date.
    """
    date: str = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"ukhsa_data_dashboard_downloads_{date}.zip"


def get_bulk_downloads_archive(
    *,
    file_format: str,
    permission_sets: PermissionSetsType | None = None,
) -> dict[str, zip]:
    """Collects all current downloads and returns a packaged zip file.

    Args:
        file_format: the format for the download response data.
        permission_sets: The permission sets extracted
            from the request of the end user.
            Defaults to None, in which case
            only downloads from public pages are collected.

    Returns:
        A dictionary containing the filename and a zip file of the
        compressed download data.
    """
    downloads = get_all_downloads(
        file_format=file_format, permission_sets=permission_sets
    )
    zip_file_name = generate_zip_filename()
    zip_file_data = write_data_to_zip(downloads=downloads)

    return {
        "zip_file_name": zip_file_name,
        "zip_file_data": zip_file_data,
    }
