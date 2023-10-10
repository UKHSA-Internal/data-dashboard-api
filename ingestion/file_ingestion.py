import io
import logging
from enum import Enum

from ingestion.consumer import Consumer

logger = logging.getLogger(__name__)


class FileIngestionFailedError(Exception):
    def __init__(self, file_name: str):
        message = f"`{file_name}` upload failed."
        super().__init__(message)


class DataSourceFileType(Enum):
    # Headline types
    headline = "headline"

    # Timeseries types
    cases = "cases"
    deaths = "deaths"
    healthcare = "healthcare"
    testing = "testing"
    vaccinations = "vaccinations"

    @classmethod
    def headline_types(cls) -> list[str]:
        return [f"{cls.headline.value}_"]

    @classmethod
    def timeseries_types(cls) -> list[str]:
        timeseries_file_types = (
            cls.cases,
            cls.deaths,
            cls.healthcare,
            cls.testing,
            cls.vaccinations,
        )
        return [
            f"{timeseries_file_type.value}_"
            for timeseries_file_type in timeseries_file_types
        ]


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


def _upload_file(filepath: str) -> None:
    logger.info("Uploading %s", filepath)

    with open(filepath, "rb") as f:
        try:
            file_ingester(file=f)
        except Exception as error:
            logger.warning("Failed upload of %s due to %s", filepath, error)
            raise FileIngestionFailedError(file_name=filepath) from error

        logger.info("Completed ingestion of %s", filepath)
