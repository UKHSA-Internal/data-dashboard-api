import io
import json
import logging
from pathlib import Path

import django

# `django.setup()` is required prior any models being imported
# This is because we spawn processes during ingestion
# primarily so that file descriptors & db connections are not
# copied from the parent as they are when `forking` instead of `spawning`.
# This is a temporary measure, once the main ingestion process is moved
# to a 1-to-1 of job:ingested file then multiprocessing can be reconfigured
django.setup()

from ingestion.utils.type_hints import INCOMING_DATA_TYPE  # noqa: E402
from ingestion.v2.consumer import Consumer  # noqa: E402

logger = logging.getLogger(__name__)


class FileIngestionFailedError(Exception):
    def __init__(self, file_name: str):
        message = f"`{file_name}` upload failed."
        super().__init__(message)


def data_ingester(data: INCOMING_DATA_TYPE) -> None:
    """Consumes the data in the given `data` and populates the database

    Args:
        data: The incoming source data to be ingested.
            Note that this is expected to be the dict
            not the file handler or stream.

    Returns:
        None

    """
    consumer = Consumer(source_data=data)

    if consumer.is_headline_data:
        return consumer.create_core_headlines()

    return consumer.create_core_and_api_timeseries()


def upload_data(key: str, data: INCOMING_DATA_TYPE) -> None:
    """Ingests the given `data` and records logs for starting and finishing points

    Args:
        key: The key of the corresponding file
        data: The incoming data to be ingested

    Returns:
        None

    """
    logger.info("Uploading %s", key)

    try:
        data_ingester(data=data)
    except Exception as error:
        logger.warning("Failed upload of %s due to %s", key, error)
        raise FileIngestionFailedError(file_name=key) from error

    logger.info("Completed ingestion of %s", key)


def _upload_data_as_file(filepath: Path) -> None:
    logger.info("Uploading %s", filepath.name)

    with open(filepath, "rb") as file:
        deserialized_data = _open_data_from_file(file=file)
        upload_data(key=filepath.name, data=deserialized_data)


def _open_data_from_file(file: io.FileIO) -> dict:
    lines = file.readlines()[0]
    return json.loads(lines)
