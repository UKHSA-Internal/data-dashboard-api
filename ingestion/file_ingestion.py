import io

from ingestion.consumer import Consumer


def file_ingester(file: io.FileIO) -> None:
    """Consumes the data in the given `file` and populates the database

    Args:
        file: The incoming source file to be consumed

    Returns:
        None

    Raises:
        `ValueError`: If the given `file` is not
            of a headline or timeseries data file type

    """
    consumer = Consumer(data=file)

    if "headline" in file.name:
        return consumer.create_headlines()

    if "timeseries" in file.name:
        return consumer.create_timeseries()

    raise ValueError()
