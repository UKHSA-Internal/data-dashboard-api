import base64
import json

import django

django.setup()


from ingestion.file_ingestion import INCOMING_DATA_TYPE  # noqa: E402
from ingestion.operations.upload import (  # noqa: E402
    ingest_data_and_post_process,
)


def decode_base64(encoded: bytes) -> str:
    """Decodes the base64 encoded bytes-like object with the utf-8 codec

    Args:
        encoded: The encoded bytes-like object

    Returns:
        The decoded string representation
        of the given base64 object

    """
    decoded_bytes = base64.b64decode(encoded)
    return decoded_bytes.decode("utf-8")


def deserialize_json(serialized: str) -> dict:
    """Deserializes the given JSON string to a Python object

    Args:
        serialized: The serialized JSON string

    Returns:
        The deserialized Python object representation
            of the given `serialized` JSON strong

    """
    return json.loads(serialized)


def extract_contents_from_record(record: dict) -> tuple[str, INCOMING_DATA_TYPE]:
    """Extracts the "name" and the "data" from the given `record`

    Notes:
        The `record` refers to a Kinesis data stream record

    Args:
        record: The incoming Kinesis data stream record

    Returns:
        Tuple containing the following:
        1) The "name" of the file,
            written to the data of the record
        2) The "data" of the contents,
            written to the data of the record

    """
    decoded_string: str = decode_base64(encoded=record["kinesis"]["data"])
    message: dict[str, str | INCOMING_DATA_TYPE] = deserialize_json(
        serialized=decoded_string
    )
    return message["name"], message["data"]


def handler(event, context) -> None:
    """Consumes incoming lambda events subscribing to the data stream

    Args:
        event: The lambda event provided by the AWS runtime.
            This contains the messages which are to be ingested
        context: The lambda context provided by the AWS runtime

    Returns:
        None

    """
    records: list[dict] = event["Records"]

    for record in records:
        key, inbound_data = extract_contents_from_record(record=record)
        ingest_data_and_post_process(data=inbound_data, key=key)
