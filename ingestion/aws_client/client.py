from ingestion.aws_client.s3_client import S3Client
from ingestion.aws_client.sqs_client import SQSClient


class AWSClient:
    """This class is the primary abstraction used to interact with AWS services

    Notes:
        Currently supports the following:
        - SQS message polling
        - Listing files in the designated ingest S3 bucket
        - Moving files in the designated ingest S3 bucket

    """

    def __init__(
        self,
        s3_client: S3Client | None = None,
        sqs_client: SQSClient | None = None,
    ):
        self.s3_client = s3_client or self.create_s3_client()
        self.sqs_client = sqs_client or self.create_sqs_client()

    # Internal client instantiation

    @classmethod
    def create_s3_client(cls) -> S3Client:
        return S3Client()

    @classmethod
    def create_sqs_client(cls) -> SQSClient:
        return SQSClient()

    # `S3Client` calls

    def list_item_keys_of_in_folder(self) -> list[str]:
        """Lists the keys of all items the `in/` folder of the s3 bucket

        Notes:
            The underlying `S3Client` is used to action this

        Returns:
            A list of keys, with each key representing a single item
            E.g:
                [
                    'COVID-19_headline_7DayAdmissions.json',
                    'influenza_testing_positivityByWeek.json',
                    ...
                ]

        """
        return self.s3_client.list_item_keys_of_in_folder()

    def download_item(self, key: str) -> str:
        """Downloads the item from the s3 bucket matching the given `key`

        Notes:
            The underlying `S3Client` is used to action this

        Args:
            key: The key of the item to be downloaded

        Returns:
            The filename associated with the item `key`

        """
        return self.s3_client.download_item(key=key)

    def move_file_to_processed_folder(self, key: str) -> None:
        """Moves the file matching the given `key` into the `processed/` folder within the s3 bucket

        Notes:
            The underlying `S3Client` is used to action this

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        return self.s3_client.move_file_to_processed_folder(key=key)

    def move_file_to_failed_folder(self, key: str) -> None:
        """Moves the file matching the given `key` into the `failed/` folder within the s3 bucket

        Notes:
            The underlying `S3Client` is used to action this

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        return self.s3_client.move_file_to_failed_folder(key=key)

    # `SQSClient` calls

    def delete_message(self, queue_url: str, message: dict) -> None:
        """Deletes the message from the specified queue.

        Notes:
            The underlying `SQSClient` is used to action this

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
        return self.sqs_client.delete_message(queue_url=queue_url, message=message)

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
        return self.sqs_client.receive_message(
            queue_url=queue_url,
            max_number_of_messages=max_number_of_messages,
            wait_time_seconds=wait_time_seconds,
            visibility_timeout=visibility_timeout,
        )
