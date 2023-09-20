import logging
import os
from typing import Optional

from ingestion.aws_client import AWSClient
from ingestion.operations.truncated_dataset import _upload_file, clear_metrics_tables

logger = logging.getLogger(__name__)


def download_files_and_upload(client: Optional[AWSClient] = None) -> None:
    """Downloads all files in the s3 bucket and ingest them

    Notes:
        Metrics tables will be cleared prior to commencing ingestion of files.
        Therefore, the files in the s3 will mirror the metrics in the database
        at the end of the ingestion process.

        After each file is ingested, it will be moved to `processed/`
        directory within the s3 bucket.

    Args:
        client: The `AWSClient` used to interact with s3.
            If not provided, the `AWSClient` will be initialized

    Returns:
        None

    """
    client = client or AWSClient()
    clear_metrics_tables()

    keys: list[str] = client.list_item_keys_of_in_folder()

    for key in keys:
        downloaded_filepath: str = client.download_item(key=key)
        _upload_file_and_remove_local_copy(filepath=downloaded_filepath)
        client.move_file_to_processed_folder(key=key)

    logger.info("Completed dataset upload")


def _upload_file_and_remove_local_copy(filepath: str):
    _upload_file(filepath=filepath)
    os.remove(filepath)
