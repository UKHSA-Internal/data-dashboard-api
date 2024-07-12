import io
import logging
import zipfile

logger = logging.getLogger(__name__)


def write_directory_to_write_stream(
    *,
    directory_name: str,
    download_group: list[dict[str, str]],
    zipf: zipfile.ZipFile,
) -> None:
    """Mutates the provided zipf in place to create a directory containing associated files.

    Args:
        directory_name: directory name for grouped downloads.
        download_group: list of dictionaries containing filename and data.
        zipf: zipfile write stream.

    Returns:
        None
    """
    try:
        for download in download_group:
            zipf.writestr(f"{directory_name}/{download['name']}", download["content"])
    except KeyError:
        logger.exception("Failed to create directory directory_name and its files.")


def write_data_to_zip(
    *,
    downloads: list[dict[str, str]],
) -> bytes:
    """Compress data into a zipfile

    Args:
        downloads: A list of dictionaries containing
            a directory name, filename and content of the data
            to be written to a zip file.

    Returns:
        A zipfile containing downloads
    """
    in_memory_zip = io.BytesIO()

    with zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        try:
            for download in downloads:
                write_directory_to_write_stream(
                    directory_name=download["directory_name"],
                    download_group=download["downloads"],
                    zipf=zipf,
                )
        except KeyError:
            logger.exception("Failed to write bulk downloads to zip write stream.")

    return in_memory_zip.getvalue()
