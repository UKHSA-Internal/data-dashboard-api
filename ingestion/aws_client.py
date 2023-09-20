import datetime
import logging

import boto3
import botocore.client

BUCKET_NAME = ""
PROFILE_NAME = ""


S3_BUCKET_ITEM_OBJECT_TYPE = dict[str, str | int | datetime.datetime]

logger = logging.getLogger(__name__)


class AWSClient:
    def __init__(self, client: botocore.client.BaseClient = None):
        boto3.setup_default_session(profile_name=PROFILE_NAME)
        self._client = client or boto3.client("s3")

    def list_contents(self) -> list[S3_BUCKET_ITEM_OBJECT_TYPE]:
        """Lists the contents of the s3 bucket

        Returns:
            A list of dicts, with each representing a single item
            E.g:
                [
                    {
                    'Key': 'COVID-19_headline_7DayAdmissions.json',
                    'LastModified': datetime.datetime(2023, 9, 20, 16, 35, 18, tzinfo=tzutc()),
                    'ETag': '"1402bb7b63597792cf4ecbaa85d037fe"',
                    'Size': 381,
                    'StorageClass':
                    'STANDARD',
                    'Owner': {'ID': 'd9bacdaa24ee8f6601775a89fb599506ec89c5cdb0a198ed4171ea96c3ae88f5'},
                    },
                    ...
                ]

        """
        bucket_contents = self._client.list_objects(Bucket=BUCKET_NAME)
        return bucket_contents["Contents"]

    def download_item(self, key: str) -> str:
        """Downloads the item from the s3 bucket matching the given `key`

        Args:
            key: The key of the item to be downloaded

        Returns:
            The input `key`

        """
        self._client.download_file(Bucket=BUCKET_NAME, Key=key, Filename=key)
        return key

    def download_all_items_in_bucket(self) -> list[str]:
        """Downloads all the items from the s3 bucket

        Returns:
            List of keys of all the items in the bucket

        """
        items: list[S3_BUCKET_ITEM_OBJECT_TYPE] = self.list_contents()
        return [self.download_item(key=item["Key"]) for item in items]

    def move_file_to_processed_folder(self, key: str) -> None:
        """Moves the file matching the given `key` into the `processed/` folder within the s3 bucket

        Args:
            key: The key of the item to be moved

        Returns:
            None

        """
        logger.info(f"Moving {key} to `processed/` in s3 bucket")
        copy_source = {"Bucket": BUCKET_NAME, "Key": key}
        self._client.copy(copy_source, BUCKET_NAME, f"processed/{key}")
        self._client.delete_object(Bucket=BUCKET_NAME, Key=key)
