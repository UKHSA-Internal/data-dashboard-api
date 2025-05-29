from unittest import mock

import botocore.client
import freezegun
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
        fake_bucket_name = "fake-bucket"
        fake_archive_bucket_name = "fake-archive-bucket"
        spy_client = aws_client_with_mocked_boto_client._client
        aws_client_with_mocked_boto_client._bucket_name = fake_bucket_name
        aws_client_with_mocked_boto_client._archive_bucket_name = (
            fake_archive_bucket_name
        )

        # When
        aws_client_with_mocked_boto_client.move_file_to_processed_folder(key=fake_key)

        # Then
        processed_key: str = aws_client_with_mocked_boto_client._build_processed_key(
            key=fake_key
        )
        # Check that the call to copy the file is made correctly
        expected_copy_file_to_processed_call = mock.call.copy(
            CopySource={"Bucket": fake_bucket_name, "Key": fake_key},
            Bucket=fake_bucket_name,
            Key=processed_key,
        )
        # Check that the call to archive the file is made correctly
        expected_copy_file_to_processed_archive_call = mock.call.copy(
            CopySource={"Bucket": fake_bucket_name, "Key": fake_key},
            Bucket=fake_archive_bucket_name,
            Key=aws_client_with_mocked_boto_client._build_processed_archive_key(
                key=fake_key
            ),
            ExtraArgs={
                "StorageClass": "GLACIER_IR",
                "MetadataDirective": "COPY",
            },
        )
        # Check that the call to delete the origin file is made correctly
        expected_delete_file_from_origin_call = mock.call.delete_object(
            Bucket=fake_bucket_name, Key=fake_key
        )
        expected_calls = [
            expected_copy_file_to_processed_call,
            expected_copy_file_to_processed_archive_call,
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

    # Tests for the `move_file_to_failed_folder()` method

    def test_move_file_to_failed_folder(
        self, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a fake key for an item
        When `move_file_to_failed_folder()`
            is called from an instance of `AWSClient`
        Then the calls are delegated to move the file
            to the failed folder

        """
        # Given
        fake_key: str = FAKE_KEY
        spy_client = aws_client_with_mocked_boto_client._client

        # When
        aws_client_with_mocked_boto_client.move_file_to_failed_folder(key=fake_key)

        # Then
        bucket_name: str = aws_client_with_mocked_boto_client._bucket_name
        failed_key: str = aws_client_with_mocked_boto_client._build_failed_key(
            key=fake_key
        )

        # Check that the call to copy the file is made correctly
        expected_copy_file_to_failed_call = mock.call.copy(
            CopySource={"Bucket": bucket_name, "Key": fake_key},
            Bucket=bucket_name,
            Key=failed_key,
        )
        # Check that the call to delete the origin file is made correctly
        expected_delete_file_from_origin_call = mock.call.delete_object(
            Bucket=bucket_name, Key=fake_key
        )
        expected_calls = [
            expected_copy_file_to_failed_call,
            expected_delete_file_from_origin_call,
        ]
        # The ordering of the call is important, we expect to copy the file
        # into the processed folder before it is deleted from the origin folder
        spy_client.assert_has_calls(calls=expected_calls, any_order=False)

    def test_move_file_to_failed_folder_records_correct_log(
        self, caplog: LogCaptureFixture, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a fake key for an item
        When `move_file_to_failed_folder()`
            is called from an instance of `AWSClient`
        Then the expected log is recorded
        """
        # Given
        fake_key: str = FAKE_KEY

        # When
        aws_client_with_mocked_boto_client.move_file_to_failed_folder(key=fake_key)

        # Then
        expected_filename: str = (
            aws_client_with_mocked_boto_client._get_filename_from_key(key=fake_key)
        )
        expected_inbound_folder: str = (
            aws_client_with_mocked_boto_client._inbound_folder
        )
        expected_failed_folder: str = aws_client_with_mocked_boto_client._failed_folder
        expected_log = (
            f"Moving `{expected_filename}` "
            f"from `{expected_inbound_folder}` "
            f"to `{expected_failed_folder}` "
            f"in s3"
        )
        assert expected_log in caplog.text

    # Tests for the _copy_file_to methods

    @mock.patch.object(AWSClient, "_build_processed_key")
    def test_copy_file_to_processed(
        self,
        spy_build_processed_key: mock.MagicMock,
        aws_client_with_mocked_boto_client: AWSClient,
    ):
        """
        Given a bucket name and a key for a file
        When `_copy_file_to_processed()` is called
            from an instance of `AWSClient`
        Then the call is delegated to the `copy` method
            on the underlying client with the correct args

        Patches:
            `spy_build_processed_key`: To check the correct
                method is called out to in order to create
                the processed key for the file

        """
        # Given
        bucket_name = "fake-bucket"
        key = FAKE_KEY
        aws_client_with_mocked_boto_client._bucket_name = bucket_name
        spy_client: mock.Mock = aws_client_with_mocked_boto_client._client

        # When
        aws_client_with_mocked_boto_client._copy_file_to_processed(key=key)

        # Then
        spy_build_processed_key.assert_called_once_with(key=key)

        spy_client.copy.assert_called_once_with(
            CopySource={"Bucket": bucket_name, "Key": key},
            Bucket=bucket_name,
            Key=spy_build_processed_key.return_value,
        )

    def test_copy_file_to_processed_records_log_when_client_error_occurs(
        self,
        aws_client_with_mocked_boto_client: AWSClient,
        caplog: LogCaptureFixture,
    ):
        """
        Given a key for a file
        And a `botocore` client which will throw a `ClientError`
        When `_copy_file_to_processed()` is called
            from an instance of `AWSClient`
        Then the error is swallowed and logged
        """
        # Given
        key: str = FAKE_KEY
        boto_client: mock.Mock = aws_client_with_mocked_boto_client._client
        boto_client.copy.side_effect = botocore.client.ClientError(
            error_response=mock.MagicMock(), operation_name=mock.MagicMock()
        )

        # When
        aws_client_with_mocked_boto_client._copy_file_to_processed(key=key)

        # Then
        processed_folder: str = aws_client_with_mocked_boto_client._processed_folder
        expected_log = f"Failed to move `{key}` to `{processed_folder}` folder"
        assert expected_log in caplog.text

    @mock.patch.object(AWSClient, "_build_failed_key")
    def test_copy_file_to_failed(
        self,
        spy_build_failed_key: mock.MagicMock,
        aws_client_with_mocked_boto_client: AWSClient,
    ):
        """
        Given a bucket name and a key for a file
        When `_copy_file_to_failed()` is called
            from an instance of `AWSClient`
        Then the call is delegated to the `copy` method
            on the underlying client with the correct args

        Patches:
            `spy_build_failed_key`: To check the correct
                method is called out to in order to create
                the failed key for the file

        """
        # Given
        bucket_name = "fake-bucket"
        key = FAKE_KEY
        aws_client_with_mocked_boto_client._bucket_name = bucket_name
        spy_client: mock.Mock = aws_client_with_mocked_boto_client._client

        # When
        aws_client_with_mocked_boto_client._copy_file_to_failed(key=key)

        # Then
        spy_build_failed_key.assert_called_once_with(key=key)

        spy_client.copy.assert_called_once_with(
            CopySource={"Bucket": bucket_name, "Key": key},
            Bucket=bucket_name,
            Key=spy_build_failed_key.return_value,
        )

    def test_copy_file_to_failed_records_log_when_client_error_occurs(
        self,
        aws_client_with_mocked_boto_client: AWSClient,
        caplog: LogCaptureFixture,
    ):
        """
        Given a key for a file
        And a `botocore` client which will throw a `ClientError`
        When `_copy_file_to_failed()` is called
            from an instance of `AWSClient`
        Then the error is swallowed and logged
        """
        # Given
        key: str = FAKE_KEY
        boto_client: mock.Mock = aws_client_with_mocked_boto_client._client
        boto_client.copy.side_effect = botocore.client.ClientError(
            error_response=mock.MagicMock(), operation_name=mock.MagicMock()
        )

        # When
        aws_client_with_mocked_boto_client._copy_file_to_failed(key=key)

        # Then
        failed_folder: str = aws_client_with_mocked_boto_client._failed_folder
        expected_log = f"Failed to move `{key}` to `{failed_folder}` folder"
        assert expected_log in caplog.text

    @mock.patch.object(AWSClient, "_build_processed_archive_key")
    def test_copy_file_to_processed_archive(
        self,
        spy_build_processed_archive_key: mock.MagicMock,
        aws_client_with_mocked_boto_client: AWSClient,
    ):
        """
        Given a bucket name and a key for a file
        When `_copy_file_to_processed_archive()` is called
            from an instance of `AWSClient`
        Then the call is delegated to the `copy` method
            on the underlying client with the correct args

        Patches:
            `spy_build_processed_archive_key`: To check the
                correct method is called out to create
                the processed archive key for the file

        """
        # Given
        bucket_name = "fake-bucket"
        archive_bucket_name = "fake-archive-bucket"
        key = FAKE_KEY
        aws_client_with_mocked_boto_client._bucket_name = bucket_name
        aws_client_with_mocked_boto_client._archive_bucket_name = archive_bucket_name
        spy_client: mock.Mock = aws_client_with_mocked_boto_client._client

        # When
        aws_client_with_mocked_boto_client._copy_file_to_processed_archive(key=key)

        # Then
        spy_build_processed_archive_key.assert_called_once_with(key=key)

        spy_client.copy.assert_called_once_with(
            CopySource={"Bucket": bucket_name, "Key": key},
            Bucket=archive_bucket_name,
            Key=spy_build_processed_archive_key.return_value,
            ExtraArgs={"StorageClass": "GLACIER_IR", "MetadataDirective": "COPY"},
        )

    def test_copy_file_to_processed_archive_records_log_when_client_error_occurs(
        self,
        aws_client_with_mocked_boto_client: AWSClient,
        caplog: LogCaptureFixture,
    ):
        """
        Given a key for a file
        And a `botocore` client which will throw a `ClientError`
        When `_copy_file_to_processed_archive()` is called
            from an instance of `AWSClient`
        Then the error is swallowed and logged
        """
        # Given
        key: str = FAKE_KEY
        boto_client: mock.Mock = aws_client_with_mocked_boto_client._client
        boto_client.copy.side_effect = botocore.client.ClientError(
            error_response=mock.MagicMock(), operation_name=mock.MagicMock()
        )

        # When
        aws_client_with_mocked_boto_client._copy_file_to_processed_archive(key=key)

        # Then
        _archive_bucket_name: str = aws_client_with_mocked_boto_client._archive_bucket_name
        expected_log = f"Failed to move `{key}` to `{_archive_bucket_name}` bucket"
        assert expected_log in caplog.text

    # Tests for `_delete_file_from_inbound`

    def test_delete_file_from_inbound_records_log_when_client_error_occurs(
        self,
        aws_client_with_mocked_boto_client: AWSClient,
        caplog: LogCaptureFixture,
    ):
        """
        Given a key for a file
        And a `botocore` client which will throw a `ClientError`
        When `_delete_file_from_inbound()` is called
            from an instance of `AWSClient`
        Then the error is swallowed and logged
        """
        # Given
        key: str = FAKE_KEY
        boto_client: mock.Mock = aws_client_with_mocked_boto_client._client
        boto_client.delete_object.side_effect = botocore.client.ClientError(
            error_response=mock.MagicMock(), operation_name=mock.MagicMock()
        )

        # When
        aws_client_with_mocked_boto_client._delete_file_from_inbound(key=key)

        # Then
        inbound_folder: str = aws_client_with_mocked_boto_client._inbound_folder
        expected_log = f"Failed to delete `{key}` from `{inbound_folder}` folder"
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
        processed_key: str = aws_client_with_mocked_boto_client._build_processed_key(
            key=fake_key
        )

        # Then
        assert processed_key == f"processed/{FAKE_FILE_NAME}"

    def test_build_failed_key(self, aws_client_with_mocked_boto_client: AWSClient):
        """
        Given a key from the s3 bucket for an item
        When `_build_failed_key()` is called
            from an instance of `AWSClient`
        Then the correct failed key is returned
        """
        # Given
        fake_key = FAKE_KEY

        # When
        failed_key: str = aws_client_with_mocked_boto_client._build_failed_key(
            key=fake_key
        )

        # Then
        assert failed_key == f"failed/{FAKE_FILE_NAME}"

    @freezegun.freeze_time("2025-01-01")
    def test_build_processed_archive_key(
        self, aws_client_with_mocked_boto_client: AWSClient
    ):
        """
        Given a key from the s3 bucket for an item
        When `_build_processed_archive_key()` is called
            from an instance of `AWSClient`
        Then the correct processed archive key is returned
        """
        # Given
        fake_key = FAKE_KEY

        # When
        processed_archive_key: str = (
            aws_client_with_mocked_boto_client._build_processed_archive_key(
                key=fake_key
            )
        )

        # Then
        expected_key = f"processed/2025-01-01/COVID-19/{FAKE_FILE_NAME}"
        assert processed_archive_key == expected_key
