import datetime

from caching.private_api.handlers import get_all_downloads
from metrics.domain.exports.zip import write_data_to_zip


def generate_zip_filename() -> str:
    """Generates a filename with today's date.

    Returns:
        A string with the downloads file name suffixed with today's date.
    """
    date: str = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"ukhsa_data_dashboard_downloads_{date}.zip"


def get_bulk_downloads_archive(file_format: str) -> dict[str, zip]:
    """Collects all current downloads and returns a packaged zip file.

    Returns:
        A dictionary containing the filename and a zip file of the
        compressed download data.
    """
    downloads = get_all_downloads(file_format=file_format)
    zip_file_name = generate_zip_filename()
    zip_file_data = write_data_to_zip(downloads=downloads)

    return {
        "zip_file_name": zip_file_name,
        "zip_file_data": zip_file_data,
    }
