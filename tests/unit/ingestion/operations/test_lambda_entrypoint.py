import base64
import json
from unittest import mock

import pytest

from ingestion.operations.lambda_entrypoint import (
    decode_base64,
    deserialize_json,
    extract_contents_from_record,
    handler,
)

MODULE_PATH = "ingestion.operations.lambda_entrypoint"


@pytest.fixture()
def incoming_message() -> dict[str, dict[str, str] | str]:
    return {
        "kinesis": {
            "partitionKey": "abc",
            "sequenceNumber": "def",
            "data": "",
        },
        "eventSource": "aws:kinesis",
        "eventVersion": "1.0",
        "eventID": "shardId-000000000000:123",
        "eventName": "aws:kinesis:record",
    }


def _create_fake_serialized_record(
    filename: str, data: dict
) -> dict[str, dict[str, str] | str]:
    input_data = {"name": filename, "data": data}
    input_data = json.dumps(input_data)
    encoded_data = base64.b64encode(bytes(input_data, "utf-8"))

    return {
        "kinesis": {
            "partitionKey": "abc",
            "sequenceNumber": "def",
            "data": encoded_data,
        },
        "eventSource": "aws:kinesis",
        "eventVersion": "1.0",
        "eventID": "shardId-000000000000:123",
        "eventName": "aws:kinesis:record",
    }


class TestDecodeBase64:
    def test_returns_correct_string(self):
        """
        Given a utf-8 encoded base64 string
        When `decode_base64()` is called
        Then the raw decoded string is returned
        """
        # Given
        fake_string = "this-is-a-fake-encoded-message"
        encoded_string: str = base64.b64encode(bytes(fake_string, "utf-8"))

        # When
        decoded: str = decode_base64(encoded=encoded_string)

        # Then
        assert decoded == fake_string


class TestDeserializeJSONT:
    def test_returns_correct_dict(self):
        """
        Given a dict serialized as a JSON string
        When `deserialize_json()` is called
        Then the raw deserialized dict is returned
        """
        # Given
        fake_expected_dict = {"a": 1, "b": 2}
        input_serialized_json = json.dumps(fake_expected_dict)

        # When
        deserialized_json = deserialize_json(serialized=input_serialized_json)

        # Then
        assert deserialized_json == fake_expected_dict


class TestExtractContentsFromMessage:
    def test_returns_correct_value(self):
        """
        Given a serialized Kinesis message containing a key and data
        When `extract_contents_from_message()` is called
        Then the correct key and data are returned
        """
        # Given
        fake_object_key = "in/abc.json"
        fake_data = {"metric": "COVID-19_cases_countRollingMean"}
        serialized_record = _create_fake_serialized_record(
            filename=fake_object_key, data=fake_data
        )

        # When
        extracted_key, extracted_data = extract_contents_from_record(
            record=serialized_record
        )

        # Then
        assert extracted_key == fake_object_key
        assert extracted_data == fake_data


class TestHandler:
    @mock.patch(f"{MODULE_PATH}.extract_contents_from_record")
    @mock.patch(f"{MODULE_PATH}.ingest_data_and_post_process")
    def test_delegates_calls_successfully(
        self,
        spy_ingest_data_and_post_process: mock.MagicMock,
        spy_extract_contents_from_record: mock.MagicMock,
    ):
        """
        Given an event containing a list of records
        When the lambda `handler()` is called
        Then the calls to the extract the data and ingest
            are properly delegated to

        Patches:
            `spy_extract_contents_from_record`: To check
                the filename key and data are extracted
                from the inbound record
            `spy_ingest_data_and_post_process`: For the
                main assertion

        """
        # Given
        mocked_records = [mock.Mock()] * 3
        fake_event = {"Records": mocked_records}

        mocked_filename = mock.Mock()
        mocked_data = mock.Mock()
        spy_extract_contents_from_record.return_value = mocked_filename, mocked_data

        # When
        handler(event=fake_event, context=mock.Mock())

        # Then
        spy_extract_contents_from_record.assert_has_calls(
            calls=[mock.call(record=mocked_record) for mocked_record in mocked_records]
        )
        spy_ingest_data_and_post_process.assert_has_calls(
            calls=[
                mock.call(data=mocked_data, key=mocked_filename)
                for fake_record in mocked_records
            ],
            any_order=True,
        )
