import logging
import os
from pathlib import Path

from ingestion.aws_client import AWSClient
from ingestion.file_ingestion import (
    INCOMING_DATA_TYPE,
    FileIngestionFailedError,
    _upload_data_as_file,
    upload_data,
)

logger = logging.getLogger(__name__)


def ingest_data_and_post_process(
    *, data: INCOMING_DATA_TYPE, key: str, client: AWSClient | None = None
) -> None:
    """Ingests the data and moves the file of the given `key` to the appropriate outbound folder in the s3 bucket

    Notes:
        If the ingest of data fails
        then the file will be moved to the `failed/` folder

    Args:
        data: The inbound data to be ingested
        key: The key of the item to be processed
        client: The `AWSClient` used to interact with s3.
            If not provided, the `AWSClient` will be initialized

    Returns:
        None

    """
    client = client or AWSClient()
    try:
        upload_data(data=data, key=key)
    except FileIngestionFailedError:
        return client.move_file_to_failed_folder(key=key)

    return client.move_file_to_processed_folder(key=key)


def _upload_file_and_remove_local_copy(*, filepath: str) -> None:
    """Ingest the file at the given `filepath` and remove from the filesystem after uploading

    Notes:
        If the file upload fails
        then the file will still be removed from the local filesystem
        before the error is re-raised.

    Args:
        filepath: The path of the file to be ingested

    Returns:
        None

    Raises:
        `FileIngestionFailedError`: If the file upload fails
            for any reason

    """
    filepath = Path(filepath)
    try:
        _upload_data_as_file(filepath=filepath)
    except FileIngestionFailedError:
        os.remove(path=filepath)
        raise
    os.remove(path=filepath)
