import io
import logging

import django

# `django.setup()` is required prior any models being imported
# This is because we spawn processes during ingestion
# primarily so that file descriptors & db connections are not
# copied from the parent as they are when `forking` instead of `spawning`.
# This is a temporary measure, once the main ingestion process is moved
# to a 1-to-1 of job:ingested file then multiprocessing can be reconfigured
django.setup()

from ingestion.consumer import Consumer  # noqa: E402
from ingestion.utils.enums import DataSourceFileType  # noqa: E402
from ingestion.utils.type_hints import INCOMING_DATA_TYPE  # noqa: E402
from ingestion.v2.consumer import ConsumerV2  # noqa: E402

logger = logging.getLogger(__name__)


class FileIngestionFailedError(Exception):
    def __init__(self, file_name: str):
        message = f"`{file_name}` upload failed."
        super().__init__(message)


def file_ingester(file: io.FileIO) -> None:
    """Consumes the data in the given `file` and populates the database

    Args:
        file: The incoming source file to be consumed

    Returns:
        None

    Raises:
        `ValueError`: If the given `file`
            does not contain 1 of the following keywords
            in the name of the given `file.name`:
                - "headline"
                - "cases"
                - "deaths"
                - "healthcare"
                - "testing"
                - "vaccinations"

    """
    consumer = Consumer(data=file)

    if any(
        headline_type in file.name
        for headline_type in DataSourceFileType.headline_types()
    ):
        return consumer.create_headlines()

    if any(
        timeseries_type in file.name
        for timeseries_type in DataSourceFileType.timeseries_types()
    ):
        return consumer.create_timeseries()

    raise ValueError


def data_ingester(data: INCOMING_DATA_TYPE) -> None:
    """Consumes the data in the given `data` and populates the database

    Args:
        data: The incoming source data to be ingested.
            Note that this is expected to be the dict
            not the file handler or stream.

    Returns:
        None

    """
    consumer = ConsumerV2(data=data)

    if consumer.is_headline_data:
        return consumer.create_core_headlines()

    return consumer.create_core_and_api_timeseries()


def _upload_file(filepath: str) -> None:
    logger.info("Uploading %s", filepath)

    with open(filepath, "rb") as f:
        try:
            file_ingester(file=f)
        except Exception as error:
            logger.warning("Failed upload of %s due to %s", filepath, error)
            raise FileIngestionFailedError(file_name=filepath) from error

        logger.info("Completed ingestion of %s", filepath)
