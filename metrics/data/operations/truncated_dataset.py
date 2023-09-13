"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the core models only.

NOTE: This contains the functionality used to seed the database with the truncated test dataset only
"""
import logging
import os
from pathlib import Path

from ingestion.file_ingestion import file_ingester
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

logger = logging.getLogger(__name__)


def _gather_test_data_source_file_paths() -> list[Path]:
    path_to_test_source_data = f"{ROOT_LEVEL_BASE_DIR}/source_data"
    source_file_names = next(os.walk(path_to_test_source_data))[2]
    return [
        Path(f"{path_to_test_source_data}/{source_file_name}")
        for source_file_name in source_file_names
        if source_file_name.endswith(".json")
    ]


def upload_test_data() -> None:
    """Uploads the truncated test data set to the database

    Notes:
        This will create records for all `CoreHeadline`, `CoreTimeSeries`
        and `APITimeSeries` tables as well as all supporting core models.

        Upload will continue even if 1 file fails to be uploaded.

    Returns:
        None

    """
    test_source_data_file_paths: list[Path] = _gather_test_data_source_file_paths()

    for test_source_data_file_path in test_source_data_file_paths:
        test_source_data_file_name: str = test_source_data_file_path.name
        logger.info(f"Uploading {test_source_data_file_name}")

        with open(test_source_data_file_path, "rb") as f:
            try:
                file_ingester(file=f)
            except Exception as error:
                logger.warning(
                    f"Failed upload of {test_source_data_file_name} due to {error}"
                )
            else:
                logger.info(f"Completed {test_source_data_file_name}")

    logger.info("Completed truncated dataset upload")
