import logging
import os
from pathlib import Path

from django.db import models

from ingestion.file_ingestion import _upload_file
from ingestion.metrics_interfaces.interface import MetricsAPIInterface
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

NOTE: This contains the functionality used to seed the database with the truncated test dataset only
"""

logger = logging.getLogger(__name__)


def _gather_test_data_source_file_paths() -> list[Path]:
    path_to_test_source_data = f"{ROOT_LEVEL_BASE_DIR}/source_data"
    source_file_names = next(os.walk(path_to_test_source_data))[2]
    return [
        Path(f"{path_to_test_source_data}/{source_file_name}")
        for source_file_name in source_file_names
        if source_file_name.endswith(".json")
    ]


def collect_all_metric_model_managers() -> tuple[models.Manager, ...]:
    """Collects all model managers associated with the metrics app"""
    return (
        MetricsAPIInterface.get_core_headline_manager(),
        MetricsAPIInterface.get_core_timeseries_manager(),
        MetricsAPIInterface.get_api_timeseries_manager(),
        MetricsAPIInterface.get_metric_manager(),
        MetricsAPIInterface.get_metric_group_manager(),
        MetricsAPIInterface.get_age_manager(),
        MetricsAPIInterface.get_geography_manager(),
        MetricsAPIInterface.get_geography_type_manager(),
        MetricsAPIInterface.get_stratum_manager(),
        MetricsAPIInterface.get_topic_manager(),
        MetricsAPIInterface.get_theme_manager(),
        MetricsAPIInterface.get_sub_theme_manager(),
    )


def clear_metrics_tables() -> None:
    """Deletes all records in the metric tables

    Returns:
         None

    """
    model_managers: tuple[models.Manager] = collect_all_metric_model_managers()

    for model_manager in model_managers:
        logger.info(f"Deleting records of {model_manager.model.__name__}")
        model_manager.all().delete()

    logger.info("Completed deleting existing metrics records")


def upload_truncated_test_data() -> None:
    """Uploads the truncated test data set to the database after clearing existing metrics records

    Notes:
        This will create records for all `CoreHeadline`, `CoreTimeSeries`
        and `APITimeSeries` tables as well as all supporting core models.

        Upload will continue even if 1 file fails to be uploaded.

        Existing metrics records will be deleted prior to the upload commencing.

    Returns:
        None

    """
    clear_metrics_tables()

    test_source_data_file_paths: list[Path] = _gather_test_data_source_file_paths()

    for test_source_data_file_path in test_source_data_file_paths:
        _upload_file(filepath=str(test_source_data_file_path))

    logger.info("Completed truncated dataset upload")
