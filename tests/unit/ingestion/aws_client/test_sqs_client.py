from unittest import mock

from ingestion.aws_client.sqs_client import SQSClient

MODULE_PATH = "ingestion.aws_client.sqs_client"


class TestSQSClient:
    @mock.patch(f"{MODULE_PATH}.boto3.client")
    def test_create_client(self, spy_boto3_client: mock.MagicMock):
        """
        Given an instance of an `SQSClient`
        When `create_client()` is called
        Then a call is made to the `boto3` library
            to create a boto3 client for SQS

        Patches:
            `spy_boto3_client`: For the main assertion
                of checking the correct call is made
                to the boto3 library
        """
        # Given
        sqs_client = SQSClient(client=mock.Mock())

        # When
        created_boto3_client = sqs_client.create_client()

        # Then
        spy_boto3_client.assert_called_once_with("sqs")
        assert created_boto3_client == spy_boto3_client.return_value

    def test_delete_message(self):
        """
        Given an SQS URL and a receipt handle
        When `delete_message()` is called
            from an instance of an `SQSClient`
        Then a call is made to the underlying boto3 client
            to delete the message
        """
        # Given
        spy_boto3_client = mock.Mock()
        sqs_client = SQSClient(client=spy_boto3_client)
        queue_url = "fake-queue-url.com"
        receipt_handle = "abc"
        message = {"ReceiptHandle": receipt_handle}

        # When
        sqs_client.delete_message(queue_url=queue_url, message=message)

        # Then
        spy_boto3_client.delete_message.assert_called_once_with(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )

    def test_receive_message(self):
        """
        Given an SQS URL
        When `receive_message()` is called
            from an instance of an `SQSClient`
        Then a call is made to the underlying boto3 client
            to receive the request number of messages
        """
        # Given
        spy_boto3_client = mock.Mock()
        sqs_client = SQSClient(client=spy_boto3_client)
        queue_url = "fake-queue-url.com"
        max_number_of_messages = 2
        wait_time_seconds = 20
        visibility_timeout = 60 * 5

        # When
        sqs_client.receive_message(
            queue_url=queue_url,
            max_number_of_messages=max_number_of_messages,
            wait_time_seconds=wait_time_seconds,
            visibility_timeout=visibility_timeout,
        )

        # Then
        spy_boto3_client.receive_message.assert_called_once_with(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
            AttributeNames=["All"],
            MessageAttributeNames=["All"],
        )
