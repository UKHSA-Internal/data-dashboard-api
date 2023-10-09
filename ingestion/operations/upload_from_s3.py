import logging
import os

from ingestion.aws_client import AWSClient
from ingestion.file_ingestion import _upload_file
from ingestion.operations.concurrency import run_with_multiple_processes
from ingestion.operations.truncated_dataset import clear_metrics_tables

logger = logging.getLogger(__name__)


def download_files_and_upload(client: AWSClient | None = None) -> None:
    """Downloads all files in the s3 bucket and ingests them

    Notes:
        Metrics tables will be cleared prior to commencing ingestion of files.
        Therefore, the files in the s3 will mirror the metrics in the database
        at the end of the ingestion process.

        After each file is ingested, it will be moved to `processed/`
        directory within the s3 bucket.

        The files are ingested in parallel with N number of processes.
        Where N is equal to the number of CPU cores on the host machine.

    Args:
        client: The `AWSClient` used to interact with s3.
            If not provided, the `AWSClient` will be initialized

    Returns:
        None

    """
    client = client or AWSClient()
    clear_metrics_tables()

    keys: list[str] = client.list_item_keys_of_in_folder()

    run_with_multiple_processes(
        upload_function=_download_file_ingest_and_teardown,
        items=keys,
    )

    logger.info("Completed dataset upload")


def _download_file_ingest_and_teardown(
    key: str, client: AWSClient | None = None
) -> None:
    """Download the file of the given `key`, ingest, remove the local copy and move to `processed/` in the s3 bucket

    Args:
        key: The key of the item to be downloaded and processed
        client: The `AWSClient` used to interact with s3.
            If not provided, the `AWSClient` will be initialized

    Returns:
        None

    """
    client = client or AWSClient()
    downloaded_filepath: str = client.download_item(key=key)
    _upload_file_and_remove_local_copy(filepath=downloaded_filepath)
    client.move_file_to_processed_folder(key=key)


def _upload_file_and_remove_local_copy(filepath: str) -> None:
    """Ingest the file at the given `filepath` and remove from the filesystem after uploading

    Args:
        filepath: The path of the file to be ingested

    Returns:
        None

    """
    _upload_file(filepath=filepath)
    os.remove(path=filepath)
