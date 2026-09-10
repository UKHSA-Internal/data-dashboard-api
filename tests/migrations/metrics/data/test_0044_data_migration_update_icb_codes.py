import logging

import importlib
import pytest

from tests.migrations.helper import MigrationTests
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory
from tests.factories.metrics.headline import CoreHeadlineFactory

logger = logging.getLogger(__name__)

migration = importlib.import_module(
    "metrics.data.migrations.0044_data_migration_updated_icb_codes"
)

GEOGRAPHIES = migration.GEOGRAPHIES


@pytest.mark.django_db(transaction=True)
class TestDataMigrationForUpdatedGeographyCodes(MigrationTests):
    previous_migration_name = (
        "0043_alter_apitimeseries_metric_value_rename_second_category"
    )
    current_migration_name = "0044_data_migration_updated_icb_codes"
    current_django_app = "data"

    def test_forward_and_then_backward_migration_resets(self):
        """
        Given the database contains existing `Geography` records
            for both East of England and North West
        And related dependencies from timeseries records
        When the new migration is applied
        Then the dependencies point to the new geography codes
        """
        # Given

        # This gets the schema up to date for test data creation
        self.migrate_backward()
        self._create_pre_existing_data()

        # Check that the existing records are as per the original names
        self._assert_data_reference_existing_geography_codes()

        # When
        self.migrate_forward()

        # Then
        self._assert_data_reference_new_geography_codes()

        # When
        self.migrate_backward()

        # Then
        self._assert_data_reference_existing_geography_codes()

    def _assert_data_references_expected_codes(self, picker):
        Geography = self.get_model("geography")  # noqa: N806
        APITimeSeries = self.get_model("apitimeseries")  # noqa: N806

        # Check that the `Geography` records have been updated as per the new names and geography codes

        for geography in GEOGRAPHIES:
            expected, unexpected = picker(geography)
            assert (
                APITimeSeries.objects.filter(
                    geography=expected["name"], geography_code=expected["code"]
                ).count()
                != 0
            )
            assert (
                APITimeSeries.objects.filter(
                    geography=unexpected["name"], geography_code=unexpected["code"]
                ).count()
                == 0
            )
            assert (
                Geography.objects.filter(
                    name=expected["name"], geography_code=expected["code"]
                ).count()
                != 0
            )
            assert (
                Geography.objects.filter(
                    name=unexpected["name"], geography_code=unexpected["code"]
                ).count()
                == 0
            )

    def _assert_data_reference_existing_geography_codes(self):
        self._assert_data_references_expected_codes(lambda x: (x["old"], x["new"]))

    def _assert_data_reference_new_geography_codes(self):
        self._assert_data_references_expected_codes(lambda x: (x["new"], x["old"]))

    def _create_pre_existing_data(self):
        for geography in GEOGRAPHIES:
            old = geography["old"]
            CoreTimeSeriesFactory.create_record(
                geography_name=old["name"], geography_code=old["code"]
            )
            CoreHeadlineFactory.create_record(
                geography=old["name"], geography_code=old["code"]
            )
            APITimeSeriesFactory.create_record(
                geography_name=old["name"], geography_code=old["code"]
            )
