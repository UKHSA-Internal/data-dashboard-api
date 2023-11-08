import logging

import boto3
import botocore.client

import config

logger = logging.getLogger(__name__)


class SQSClient:
    """This class is used to interact with the SQS service to poll for messages

    Notes:
        Primarily used to poll SQS for messages related to new data
        which is to be ingested

    """

    def __init__(
        self,
        client: botocore.client.BaseClient | None = None,
        sqs_url: str = config.SQS_QUEUE_URL,
    ):
        self._client = client or self.create_client()
        self._sqs_url = sqs_url

    @classmethod
    def create_client(cls) -> botocore.client.BaseClient:
        """Creates a boto3 client instance connected to sqs

        Returns:
            A boto3 client instance for sqs

        """
        return boto3.client("sqs")

    def delete_message(self, queue_url: str, message: dict) -> None:
        """Deletes the message from the specified queue.

        Args:
            queue_url: The URL of the SQS service (managed queue)
            message: The message containing a `ReceiptHandle`
                which is used to delete the message

        Returns:
            None

        Raises:
            KeyError: If the "ReceiptHandle" key is not present
                in the provided `message`

        """
        receipt_handle: str = message["ReceiptHandle"]
        self._client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    def receive_message(
        self,
        queue_url: str,
        max_number_of_messages: int,
        wait_time_seconds: int,
        visibility_timeout: int,
    ) -> dict:
        """Receives the message(s) from the specified SQS service (managed queue) of the given `queue_url`.

        Args:
            queue_url: The URL of the SQS service (managed queue)
            max_number_of_messages: The maximum number of messages
                to retrieve from the queue.
                Must be an integer between 1 and 10.
            wait_time_seconds: The duration for which the call waits
                for a message to arrive in the queue before returning.
                If a message is available, the call will return sooner.
                If no messages are available and the wait time expires,
                the call returns successfully with an empty list of messages.
            visibility_timeout: The duration (in seconds) that the received messages
                are hidden from subsequent retrieve requests after being retrieved.
                For example, if 1 worker/client retrieves a message from the queue,
                the `visibility_timeout` controls how long that message is not allowed
                to be retrieved by other workers/clients.
                This is in place to prevent multiple workers retrieving the same message.

        Returns:
            None

        """
        return self._client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=["All"],
            MaxNumberOfMessages=max_number_of_messages,
            MessageAttributeNames=["All"],
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
        )
