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


class S3Client:
    """This class is used to interact with the designated s3 bucket

    Notes:
        Primarily used to list files in the designated inbound folder in the bucket.
        As well as to download them and move them to the designated outbound folder

    """

    def __init__(
        self,
        client: botocore.client.BaseClient | None = None,
        profile_name: str = config.AWS_PROFILE_NAME,
        bucket_name: str = config.INGESTION_BUCKET_NAME,
        inbound_folder: str = DEFAULT_INBOUND_INGESTION_FOLDER,
        processed_folder: str = DEFAULT_PROCESSED_INGESTION_FOLDER,
        failed_folder: str = DEFAULT_FAILED_INGESTION_FOLDER,
    ):
        self._client = client or self.create_client(profile_name=profile_name)
        self._bucket_name = bucket_name
        self._inbound_folder = inbound_folder
        self._processed_folder = processed_folder
        self._failed_folder = failed_folder

    @classmethod
    def create_client(cls, profile_name: str) -> botocore.client.BaseClient:
        """Creates a boto3 client instance connected to s3

        Returns:
            A boto3 client instance for s3

        """
        if profile_name:
            boto3.setup_default_session(profile_name=profile_name)
        return boto3.client("s3")

    def list_item_keys_of_in_folder(self) -> list[str]:
        """Lists the keys of all items the `in/` folder of the s3 bucket

        Returns:
            A list of keys, with each key representing a single item
            E.g:
                [
                    'COVID-19_headline_7DayAdmissions.json',
                    'influenza_testing_positivityByWeek.json',
                    ...
                ]

        """
        bucket_objects: list[S3_BUCKET_ITEM_OBJECT_TYPE] = self._client.list_objects_v2(
            Bucket=self._bucket_name, Prefix=self._inbound_folder
        )
        bucket_contents: list[S3_BUCKET_ITEM_OBJECT_TYPE] = bucket_objects["Contents"]

        return [
            bucket_item["Key"]
            for bucket_item in bucket_contents
            if bucket_item["Key"].endswith(".json")
        ]

    def download_item(self, key: str) -> str:
        """Downloads the item from the s3 bucket matching the given `key`

        Args:
            key: The key of the item to be downloaded

        Returns:
            The filename associated with the item `key`

        """
        filename: str = self._get_filename_from_key(key=key)
        logger.info("Downloading %s from s3", filename)
        self._client.download_file(Bucket=self._bucket_name, Key=key, Filename=filename)
        return filename

    def move_file_to_processed_folder(self, key: str) -> None:
        """Moves the file matching the given `key` into the `processed/` folder within the s3 bucket

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
        self._delete_file_from_inbound(key=key)

    def move_file_to_failed_folder(self, key: str) -> None:
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

    def _copy_file_to_processed(self, key: str) -> None:
        """Copies the file matching the given `key` into the processed folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        self._client.copy(
            CopySource={"Bucket": self._bucket_name, "Key": key},
            Bucket=self._bucket_name,
            Key=self._build_processed_key(key=key),
        )

    def _copy_file_to_failed(self, key: str) -> None:
        """Copies the file matching the given `key` into the failed folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        self._client.copy(
            CopySource={"Bucket": self._bucket_name, "Key": key},
            Bucket=self._bucket_name,
            Key=self._build_failed_key(key=key),
        )

    def _delete_file_from_inbound(self, key: str) -> None:
        """Deletes the file matching the given `key` from the inbound folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        self._client.delete_object(Bucket=self._bucket_name, Key=key)

    def _get_filename_from_key(self, key: str) -> str:
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

    def _build_destination_key(self, key: str, folder: str) -> str:
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

    def _build_failed_key(self, key: str) -> str:
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
