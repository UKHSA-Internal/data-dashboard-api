import io
import logging
import zipfile

logger = logging.getLogger(__name__)


def write_data_to_zip(
    downloads: list[dict[str, str]],
) -> zip:
    """Compress data into a zipfile

    Args:
        downloads: A list of dictionaries containing
            a name and content of the data to be written to a zip file

    Returns:
        A zipfile containing downloads
    """
    in_memory_zip = io.BytesIO()

    with zipfile.ZipFile(in_memory_zip, "w") as zipf:
        try:
            for download in downloads:
                zipf.writestr(download["name"], download["content"])
        except KeyError:
            logger.exception("Failed to write bulk_downloads to zip write stream")

    return in_memory_zip.getvalue()
