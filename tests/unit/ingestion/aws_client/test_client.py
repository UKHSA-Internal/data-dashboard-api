from unittest import mock

import pytest

from ingestion.aws_client.client import AWSClient

FAKE_FILE_NAME = "COVID-19_headline_ONSdeaths_7DayChange.json"
FAKE_KEY = f"in/{FAKE_FILE_NAME}"


@pytest.fixture
def aws_client_with_mocked_clients() -> AWSClient:
    return AWSClient(
        s3_client=mock.Mock(),
        sqs_client=mock.Mock(),
    )


class TestAWSClient:
    # Tests for the `__init__` method

    @mock.patch.object(AWSClient, "create_s3_client")
    def test_create_s3_client_called_if_not_provided(
        self, spy_create_s3_client: mock.Mock
    ):
        """
        Given no provided `S3Client`
        When an instance of `AWSClient` is initialized
        Then the `create_s3_client()` method is called
            to set the underlying s3 client

        Patches:
            `spy_create_s3_client`: For the main assertion
                of checking the correct method is delegated
                to for setting a default s3 client
        """
        # Given
        no_s3_client = None

        # When
        aws_client = AWSClient(sqs_client=mock.Mock(), s3_client=no_s3_client)

        # Then
        spy_create_s3_client.assert_called_once()
        aws_client.s3_client = spy_create_s3_client.return_value

    @mock.patch.object(AWSClient, "create_sqs_client")
    def test_create_sqs_client_called_if_not_provided(
        self, spy_create_sqs_client: mock.Mock
    ):
        """
        Given no provided `SQSClient`
        When an instance of `AWSClient` is initialized
        Then the `create_sqs_client()` method is called
            to set the underlying sqs client

        Patches:
            `spy_create_sqs_client`: For the main assertion
                of checking the correct method is delegated
                to for setting a default sqs client
        """
        # Given
        no_sqs_client = None

        # When
        aws_client = AWSClient(sqs_client=no_sqs_client, s3_client=mock.Mock())

        # Then
        spy_create_sqs_client.assert_called_once()
        aws_client.s3_client = spy_create_sqs_client.return_value

    # `S3Client` calls
    def test_list_item_keys_of_in_folder_delegates_call(
        self, aws_client_with_mocked_clients: AWSClient
    ):
        """
        Given an `AWSClient` with a mocked `S3Client`
        When `list_item_keys_of_in_folder()`
            is called from the `AWSClient` instance
        Then the call is delegated to the underlying `S3Client` instance
        """
        # Given
        s3_client = aws_client_with_mocked_clients.s3_client

        # When
        aws_client_with_mocked_clients.list_item_keys_of_in_folder()

        # Then
        s3_client.list_item_keys_of_in_folder.assert_called_once()

    def test_download_item_delegates_call(
        self, aws_client_with_mocked_clients: AWSClient
    ):
        """
        Given an `AWSClient` with a mocked `S3Client`
        When `download_item()` is called from the `AWSClient` instance
        Then the call is delegated to the underlying `S3Client` instance
        """
        # Given
        fake_key = FAKE_KEY
        s3_client = aws_client_with_mocked_clients.s3_client

        # When
        aws_client_with_mocked_clients.download_item(key=fake_key)

        # Then
        s3_client.download_item.assert_called_once_with(key=fake_key)

    def test_move_file_to_failed_folder_delegates_call(
        self, aws_client_with_mocked_clients: AWSClient
    ):
        """
        Given an `AWSClient` with a mocked `S3Client`
        When `move_file_to_failed_folder()`
            is called from the `AWSClient` instance
        Then the call is delegated to the underlying `S3Client` instance
        """
        # Given
        fake_key = FAKE_KEY
        s3_client = aws_client_with_mocked_clients.s3_client

        # When
        aws_client_with_mocked_clients.move_file_to_failed_folder(key=fake_key)

        # Then
        s3_client.move_file_to_failed_folder.assert_called_once_with(key=fake_key)

    def test_move_file_to_processed_folder_delegates_call(
        self, aws_client_with_mocked_clients: AWSClient
    ):
        """
        Given an `AWSClient` with a mocked `S3Client`
        When `move_file_to_processed_folder()`
            is called from the `AWSClient` instance
        Then the call is delegated to the underlying `S3Client` instance
        """
        # Given
        fake_key = FAKE_KEY
        s3_client = aws_client_with_mocked_clients.s3_client

        # When
        aws_client_with_mocked_clients.move_file_to_processed_folder(key=fake_key)

        # Then
        s3_client.move_file_to_processed_folder.assert_called_once_with(key=fake_key)

    # `SQSClient` calls

    def test_receive_message(self, aws_client_with_mocked_clients: AWSClient):
        """
        Given an `AWSClient` with a mocked `SQSClient`
        When `receive_message()` is called from the `AWSClient` instance
        Then the call is delegated to the underlying `SQSClient` instance
        """
        # Given
        mocked_queue_url = mock.Mock()
        max_number_of_messages = 1
        wait_time_seconds = 20
        visibility_timeout = 60 * 2
        sqs_client = aws_client_with_mocked_clients.sqs_client

        # When
        aws_client_with_mocked_clients.receive_message(
            queue_url=mocked_queue_url,
            max_number_of_messages=max_number_of_messages,
            wait_time_seconds=wait_time_seconds,
            visibility_timeout=visibility_timeout,
        )

        # Then
        sqs_client.receive_message.assert_called_once_with(
            queue_url=mocked_queue_url,
            max_number_of_messages=max_number_of_messages,
            wait_time_seconds=wait_time_seconds,
            visibility_timeout=visibility_timeout,
        )

    def test_delete_message(self, aws_client_with_mocked_clients: AWSClient):
        """
        Given an `AWSClient` with a mocked `SQSClient`
        When `delete_message()` is called from the `AWSClient` instance
        Then the call is delegated to the underlying `SQSClient` instance
        """
        # Given
        mocked_queue_url = mock.Mock()
        mocked_message = mock.Mock()
        sqs_client = aws_client_with_mocked_clients.sqs_client

        # When
        aws_client_with_mocked_clients.delete_message(
            queue_url=mocked_queue_url, message=mocked_message
        )

        # Then
        sqs_client.delete_message.assert_called_once_with(
            queue_url=mocked_queue_url, message=mocked_message
        )
