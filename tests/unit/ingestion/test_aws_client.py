from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from ingestion.aws_client import AWSClient

MODULE_PATH = "ingestion.aws_client"

FAKE_FILE_NAME = "COVID-19_headline_ONSdeaths_7DayChange.json"
FAKE_KEY = f"in/{FAKE_FILE_NAME}"


@pytest.fixture
def aws_client_with_mocked_boto_client() -> AWSClient:
    return AWSClient(client=mock.Mock())


class TestAWSClient:
    # Tests for the `__init__`
    @mock.patch.object(AWSClient, "create_client")
    def test_create_client_called_when_client_not_provided(
        self, spy_create_client: mock.MagicMock
    ):
        """
        Given no provided boto3 client
        When an instance of `AWSClient` is created
        Then the `create_client()` method is called

        Patches:
            `spy_create_client`: For the main assertion
                and to check this created client is
                set on the `AWSClient` object

        """
        # Given
        no_boto3_client = None

        # When
        aws_client = AWSClient(client=no_boto3_client)

        # Then
        spy_create_client.assert_called_once()
        assert aws_client._client == spy_create_client.return_value

    def test_inbound_folder_defaults_to_expected_value(self):
        """
        Given a mocked boto3 client object
        When an instance of `AWSClient` is created
        Then the correct default inbound folder is set
        """
        # Given
        mocked_boto3_client = mock.Mock()

        # When
        aws_client = AWSClient(client=mocked_boto3_client)

        # Then
        assert aws_client._inbound_folder == "in/"

    def test_processed_folder_defaults_to_expected_value(self):
        """
        Given a mocked boto3 client object
        When an instance of `AWSClient` is created
        Then the correct default processed folder is set
        """
        # Given
        mocked_boto3_client = mock.Mock()

        # When
        aws_client = AWSClient(client=mocked_boto3_client)

        # Then
        assert aws_client._processed_folder == "processed/"

    def test_failed_folder_defaults_to_expected_value(self):
        """
        Given a mocked boto3 client object
        When an instance of `AWSClient` is created
        Then the correct default failed folder is set
        """
        # Given
        mocked_boto3_client = mock.Mock()

        # When
        aws_client = AWSClient(client=mocked_boto3_client)

        # Then
        assert aws_client._failed_folder == "failed/"

    @mock.patch(f"{MODULE_PATH}.boto3")
    def test_create_client(self, spy_boto3: mock.MagicMock):
        """
        Given an AWS profile name
        When `create_client()` is called from the `AWSClient` class
        Then a boto3 client is created with the provided profile name

        Patches:
            `spy_boto3`: For the main assertions
                and to check the `boto3` library
                is used correctly to create the boto3 client

        """
        # Given
        aws_profile_name = "fake-aws-profile-name"

        boto3_client = AWSClient.create_client(profile_name=aws_profile_name)

        # Then
        spy_boto3.setup_default_session.assert_called_once_with(
            profile_name=aws_profile_name
        )
        assert boto3_client == spy_boto3.client.return_value

    @mock.patch(f"{MODULE_PATH}.boto3")
    def test_create_client_does_not_setup_default_session_for_no_profile_name(
        self, spy_boto3: mock.MagicMock
    ):
        """
        Given no provided AWS profile name
        When `create_client()` is called from the `AWSClient` class
        Then a boto3 client is created
        And a default session is not setup with any profile name

        Patches:
            `spy_boto3`: For the main assertions
                and to check the `boto3` library
                is used correctly to create the boto3 client

        """
        # Given
        no_aws_profile_name = ""

        boto3_client = AWSClient.create_client(profile_name=no_aws_profile_name)

        # Then
        spy_boto3.setup_default_session.assert_not_called()
        assert boto3_client == spy_boto3.client.return_value

    # Tests for the `list_item_keys_of_in_folder()` method

    def test_list_item_keys_of_in_folder(
        self, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a response from listing objects in a s3 bucket
        When `list_item_keys_of_in_folder()` is called
            from an instance of `AWSClient`
        Then the correct list of object keys is returned
        """
        # Given
        expected_key = "in/influenza_healthcare_ICUHDUadmissionRateByWeek.json"
        fake_returned_bucket_objects = {
            "ResponseMetadata": {
                "RequestId": "K8NQXPBZ44GF4HP2",
                "HTTPStatusCode": 200,
            },
            "Contents": [
                {
                    "Key": "in/",
                    "Size": 0,
                },
                {
                    "Key": expected_key,
                    "Size": 199104,
                },
            ],
            "Name": "uhd-d06bcac6-ingest",
            "Prefix": "in/",
            "MaxKeys": 1000,
        }
        mocked_boto3_client = aws_client_with_mocked_boto_client._client
        mocked_boto3_client.list_objects_v2.return_value = fake_returned_bucket_objects

        # When
        keys: list[
            str
        ] = aws_client_with_mocked_boto_client.list_item_keys_of_in_folder()

        # Then
        assert keys == [expected_key]

    def test_list_item_keys_of_in_folder_only_includes_json_files(
        self, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a response from listing objects in a s3 bucket which contains
            a mixture of json & csv files
        When `list_item_keys_of_in_folder()` is called
            from an instance of `AWSClient`
        Then only the keys of json files are returned
        """
        # Given
        key_for_json_file = "in/influenza_healthcare_ICUHDUadmissionRateByWeek.json"
        key_for_csv_file = "in/influenza_healthcare_ICUHDUadmissionRateByWeek.csv"
        fake_returned_bucket_objects = {
            "ResponseMetadata": {
                "RequestId": "K8NQXPBZ44GF4HP2",
                "HTTPStatusCode": 200,
            },
            "Contents": [
                {
                    "Key": "in/",
                    "Size": 0,
                },
                {
                    "Key": key_for_json_file,
                    "Size": 199104,
                },
                {
                    "Key": key_for_csv_file,
                    "Size": 199104,
                },
            ],
            "Name": "uhd-d06bcac6-ingest",
            "Prefix": "in/",
            "MaxKeys": 1000,
        }
        mocked_boto3_client = aws_client_with_mocked_boto_client._client
        mocked_boto3_client.list_objects_v2.return_value = fake_returned_bucket_objects

        # When
        keys: list[
            str
        ] = aws_client_with_mocked_boto_client.list_item_keys_of_in_folder()

        # Then
        assert key_for_json_file in keys
        assert key_for_csv_file not in keys

    # Tests for the `download_item()` method

    @mock.patch.object(AWSClient, "_get_filename_from_key")
    def test_download_item(
        self,
        spy_get_filename_from_key: mock.MagicMock,
        aws_client_with_mocked_boto_client: AWSClient,
    ):
        """
        Given a fake key for an item
        When `download_item()` is called from an instance of `AWSClient`
        Then the call is delegated to `download_file()`
            on the underlying client

        Patches:
            `spy_get_filename_from_key`: To isolate the extracted
                filename and check that is being passed to the
                `download_file()` method call of the underlying client

        """
        # Given
        fake_key: str = FAKE_KEY
        spy_client = aws_client_with_mocked_boto_client._client

        # When
        filename: str = aws_client_with_mocked_boto_client.download_item(key=fake_key)

        # Then
        expected_filename = spy_get_filename_from_key.return_value
        spy_client.download_file.assert_called_once_with(
            Bucket=aws_client_with_mocked_boto_client._bucket_name,
            Key=fake_key,
            Filename=expected_filename,
        )
        assert filename == expected_filename

    def test_download_item_records_correct_log(
        self, caplog: LogCaptureFixture, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a fake key for an item
        When `download_item()` is called from an instance of `AWSClient`
        Then the expected log is recorded
        """
        # Given
        fake_key: str = FAKE_KEY

        # When
        aws_client_with_mocked_boto_client.download_item(key=fake_key)

        # Then
        expected_filename = aws_client_with_mocked_boto_client._get_filename_from_key(
            key=fake_key
        )
        assert f"Downloading {expected_filename} from s3" in caplog.text

    # Tests for the `move_file_to_processed_folder()` method

    def test_move_file_to_processed_folder(
        self, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a fake key for an item
        When `move_file_to_processed_folder()`
            is called from an instance of `AWSClient`
        Then the calls are delegated to move the file
            to the processed folder
        """
        # Given
        fake_key: str = FAKE_KEY
        spy_client = aws_client_with_mocked_boto_client._client

        # When
        aws_client_with_mocked_boto_client.move_file_to_processed_folder(key=fake_key)

        # Then
        bucket_name: str = aws_client_with_mocked_boto_client._bucket_name
        processed_key: str = (
            aws_client_with_mocked_boto_client._build_processed_key(key=fake_key)
        )
        # Check that the call to copy the file is made correctly
        expected_copy_file_to_processed_call = mock.call.copy(
            CopySource={"Bucket": bucket_name, "Key": fake_key},
            Bucket=bucket_name,
            Key=processed_key,
        )
        # Check that the call to delete the origin file is made correctly
        expected_delete_file_from_origin_call = mock.call.delete_object(
            Bucket=bucket_name, Key=fake_key
        )
        expected_calls = [
            expected_copy_file_to_processed_call,
            expected_delete_file_from_origin_call,
        ]
        # The ordering of the call is important, we expect to copy the file
        # into the processed folder before it is deleted from the origin folder
        spy_client.assert_has_calls(calls=expected_calls, any_order=False)

    def test_move_file_to_processed_folder_records_correct_log(
        self, caplog: LogCaptureFixture, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a fake key for an item
        When `move_file_to_processed_folder()`
            is called from an instance of `AWSClient`
        Then the expected log is recorded
        """
        # Given
        fake_key: str = FAKE_KEY

        # When
        aws_client_with_mocked_boto_client.move_file_to_processed_folder(key=fake_key)

        # Then
        expected_filename: str = (
            aws_client_with_mocked_boto_client._get_filename_from_key(key=fake_key)
        )
        expected_inbound_folder: str = (
            aws_client_with_mocked_boto_client._inbound_folder
        )
        expected_processed_folder: str = (
            aws_client_with_mocked_boto_client._processed_folder
        )
        expected_log = (
            f"Moving `{expected_filename}` "
            f"from `{expected_inbound_folder}` "
            f"to `{expected_processed_folder}` "
            f"in s3"
        )
        assert expected_log in caplog.text

    # Tests for utility methods

    def test_get_filename_from_key(self, aws_client_with_mocked_boto_client: AWSClient):
        """
        Given a key from the s3 bucket for an item
        When `_get_filename_from_key()` is called
            from an instance of `AWSClient`
        Then the filename is returned
        """
        # Given
        key = FAKE_KEY
        # The key is the full path within the s3 bucket
        # This is similar to a filepath as we would see it on a filesystem

        # When
        filename: str = aws_client_with_mocked_boto_client._get_filename_from_key(
            key=key
        )

        # Then
        assert filename == FAKE_FILE_NAME

    def test_build_processed_key(self, aws_client_with_mocked_boto_client: AWSClient):
        """
        Given a key from the s3 bucket for an item
        When `_build_processed_key()` is called
            from an instance of `AWSClient`
        Then the correct processed key is returned
        """
        # Given
        fake_key = FAKE_KEY

        # When
        processed_key: str = (
            aws_client_with_mocked_boto_client._build_processed_key(key=fake_key)
        )

        # Then
        assert processed_key == f"processed/{FAKE_FILE_NAME}"
