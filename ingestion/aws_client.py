import logging
from typing import Optional

import boto3
import botocore.client

BUCKET_NAME = ""
PROFILE_NAME = ""

FOLDER_TO_COLLECT_FILES_FROM = "in/"
FOLDER_TO_MOVE_COMPLETED_FILES_TO = "processed/"

logger = logging.getLogger(__name__)


class AWSClient:
    def __init__(self, client: Optional[botocore.client.BaseClient] = None):
        boto3.setup_default_session(profile_name=PROFILE_NAME)
        self._client = client or boto3.client("s3")

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
        bucket_objects = self._client.list_objects(
            Bucket=BUCKET_NAME, Prefix=FOLDER_TO_COLLECT_FILES_FROM
        )
        bucket_contents = bucket_objects["Contents"]
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
            The input `key`

        """
        filename = key.split(FOLDER_TO_COLLECT_FILES_FROM)[1]
        self._client.download_file(Bucket=BUCKET_NAME, Key=key, Filename=filename)
        return filename

    def move_file_to_processed_folder(self, key: str) -> None:
        """Moves the file matching the given `key` into the `processed/` folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        logger.info(f"Moving `{key}` to `processed/` in s3 bucket")
        copy_source = {"Bucket": BUCKET_NAME, "Key": key}
        self._client.copy(
            copy_source, BUCKET_NAME, f"{FOLDER_TO_MOVE_COMPLETED_FILES_TO}/{key}"
        )
        self._client.delete_object(Bucket=BUCKET_NAME, Key=key)
