import datetime
import logging

import boto3
import botocore.client

import config

DEFAULT_INBOUND_INGESTION_FOLDER = "in/"
DEFAULT_PROCESSED_INGESTION_FOLDER = "processed/"
DEFAULT_FAILED_INGESTION_FOLDER = "failed/"

logger = logging.getLogger(__name__)

S3_BUCKET_ITEM_OBJECT_TYPE = dict[str, str | int | datetime.datetime]


class AWSClient:
    """This class is used to interact with the designated s3 bucket

    Notes:
        Primarily used to list files in the designated inbound folder in the bucket.
        As well as to download them and move them to the designated outbound folder.
        Proccessed files are also copied to the archive bucket.

    """

    def __init__(
        self,
        *,
        client: botocore.client.BaseClient | None = None,
        profile_name: str = config.AWS_PROFILE_NAME,
        bucket_name: str = config.INGESTION_BUCKET_NAME,
        archive_bucket_name: str = config.INGESTION_ARCHIVE_BUCKET_NAME,
        inbound_folder: str = DEFAULT_INBOUND_INGESTION_FOLDER,
        processed_folder: str = DEFAULT_PROCESSED_INGESTION_FOLDER,
        failed_folder: str = DEFAULT_FAILED_INGESTION_FOLDER,
    ):
        self._client = client or self.create_client(profile_name=profile_name)
        self._bucket_name = bucket_name
        self._archive_bucket_name = archive_bucket_name
        self._inbound_folder = inbound_folder
        self._processed_folder = processed_folder
        self._failed_folder = failed_folder

    @classmethod
    def create_client(cls, *, profile_name: str) -> botocore.client.BaseClient:
        """Creates a boto3 client instance connected to s3

        Returns:
            A boto3 client instance for s3

        """
        if profile_name:
            boto3.setup_default_session(profile_name=profile_name)
        return boto3.client("s3")

    def move_file_to_processed_folder(self, *, key: str) -> None:
        """Moves the file matching the given `key` into the `processed/` folder within the s3 bucket

        Notes:
            This will also copy the file
            to the proccessed folder in the archive s3 bucket.

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        filename: str = self._get_filename_from_key(key=key)
        logger.info(
            "Moving `%s` from `%s` to `%s` in s3",
            filename,
            self._inbound_folder,
            self._processed_folder,
        )
        self._copy_file_to_processed(key=key)
        self._copy_file_to_processed_archive(key=key)
        self._delete_file_from_inbound(key=key)

    def move_file_to_failed_folder(self, *, key: str) -> None:
        """Moves the file matching the given `key` into the `failed/` folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        filename: str = self._get_filename_from_key(key=key)
        logger.info(
            "Moving `%s` from `%s` to `%s` in s3",
            filename,
            self._inbound_folder,
            self._failed_folder,
        )
        self._copy_file_to_failed(key=key)
        self._delete_file_from_inbound(key=key)

    def _copy_file_to_processed(self, *, key: str) -> None:
        """Copies the file matching the given `key` into the processed folder within the s3 bucket

        Notes:
            If more than 1 client is consuming a file,
            then we can run into race conditions,
            whereby a client is trying to move a file
            which has already been moved.
            In this case, the `ClientError`
            will be swallowed and logged.

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        try:
            self._client.copy(
                CopySource={"Bucket": self._bucket_name, "Key": key},
                Bucket=self._bucket_name,
                Key=self._build_processed_key(key=key),
            )
        except botocore.client.ClientError:
            logger.warning(
                "Failed to move `%s` to `%s` folder", key, self._processed_folder
            )

    def _copy_file_to_processed_archive(self, *, key: str) -> None:
        """Copies the file matching the given `key` into the ingest archive s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        processed_archive_key: str = self._build_processed_archive_key(key=key)
        try:
            self._client.copy(
                CopySource={"Bucket": self._bucket_name, "Key": key},
                Bucket=self._archive_bucket_name,
                Key=processed_archive_key,
                ExtraArgs={
                    "StorageClass": "GLACIER_IR",
                    "MetadataDirective": "COPY",
                },
            )
        except botocore.client.ClientError:
            logger.warning(
                "Failed to move `%s` to `%s` bucket", key, self._archive_bucket_name
            )

    def _copy_file_to_failed(self, *, key: str) -> None:
        """Copies the file matching the given `key` into the failed folder within the s3 bucket

        Notes:
            If more than 1 client is consuming a file,
            then we can run into race conditions,
            whereby a client is trying to move a file
            which has already been moved.
            In this case, the `ClientError`
            will be swallowed and logged.

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        try:
            self._client.copy(
                CopySource={"Bucket": self._bucket_name, "Key": key},
                Bucket=self._bucket_name,
                Key=self._build_failed_key(key=key),
            )
        except botocore.client.ClientError:
            logger.warning(
                "Failed to move `%s` to `%s` folder", key, self._failed_folder
            )

    def _delete_file_from_inbound(self, *, key: str) -> None:
        """Deletes the file matching the given `key` from the inbound folder within the s3 bucket

        Notes:
            If more than 1 client is consuming a file,
            then we can run into race conditions,
            whereby a client is trying to delete a file
            which has already been moved.
            In this case, the `ClientError`
            will be swallowed and logged.

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        try:
            self._client.delete_object(Bucket=self._bucket_name, Key=key)
        except botocore.client.ClientError:
            logger.warning(
                "Failed to delete `%s` from `%s` folder", key, self._inbound_folder
            )

    def _get_filename_from_key(self, *, key: str) -> str:
        """Extracts the filename from the `key`

        Examples:
            If the inbound `key` of "in/abc.json" is provided,
            then "abc.json" will be returned

        Args:
            key: The inbound key of the item in the bucket

        Returns:
            The filename associated with the item

        """
        return key.split(self._inbound_folder)[1]

    def _build_destination_key(self, *, key: str, folder: str) -> str:
        filename: str = self._get_filename_from_key(key=key)
        return f"{folder}{filename}"

    def _build_processed_key(self, key: str) -> str:
        """Constructs the full processed `key` of the item

        Examples:
            If the inbound `key` of "in/abc.json" is provided,
            then "processed/abc.json" will be returned

        Args:
            key: The inbound key of the item in the bucket

        Returns:
            The processed key of the item

        """
        return self._build_destination_key(key=key, folder=self._processed_folder)

    def _build_failed_key(self, *, key: str) -> str:
        """Constructs the full failed `key` of the item

        Examples:
            If the inbound `key` of "in/abc.json" is provided,
            then "failed/abc.json" will be returned

        Args:
            key: The inbound key of the item in the bucket

        Returns:
            The failed key of the item

        """
        return self._build_destination_key(key=key, folder=self._failed_folder)

    def _build_processed_archive_key(self, key: str) -> str:
        """Constructs the full archive proccesed `key` of the item

        Examples:
            If the inbound `key` of
            "in/adenovirus_testing_positivityByWeek_CTRY_E92000001_all_all_default.json" is provided,
            then "2025-05-29/adenovirus/adenovirus_testing_positivityByWeek_CTRY_E92000001_all_all_default.json"
            will be returned where the current date is "2025-05-29".

        Args:
            key: The inbound key of the item in the bucket

        Returns:
            The archive key of the item

        """
        filename: str = self._get_filename_from_key(key=key)
        topic = filename.split("_", maxsplit=1)[0]
        current_date: str = datetime.datetime.now().strftime("%Y-%m-%d")
        return f"processed/{current_date}/{topic}/{filename}"
