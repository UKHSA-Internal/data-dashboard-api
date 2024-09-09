import datetime

import pytest

from tests.migrations.helper import MigrationTests

EAST_OF_ENGLAND = "East of England"
NORTH_WEST = "North West"
NHS_REGION = "NHS Region"

NHS_REGIONS_UPDATE_LOOKUP = {
    EAST_OF_ENGLAND: {"old_code": "E40000007", "new_code": "E40000013"},
    NORTH_WEST: {"old_code": "E40000010", "new_code": "E40000014"},
}


@pytest.mark.django_db(transaction=True)
class Test0032DataMigrationForUpdatedGeographyCodes(MigrationTests):
    previous_migration_name = "0031_add_composite_index_for_api_timeseries"
    current_migration_name = "0032_data_migration_for_updated_geography_codes"
    current_django_app = "data"

    def test_forward_and_then_backward_migration(self):
        """
        Given the database contains existing `Geography` records
            for both St Helens and Mersey
        And related dependencies from headline and timeseries
        When the new migration is applied
        Then the dependencies point to Mersey record
        And the St Helens `Geography` record is deleted
        """
        # Given
        self.migrate_backward()
        self._create_all_pre_existing_models()
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        APITimeSeries = self.get_model("apitimeseries")

        # Check that the existing records are as per the original names
        assert Geography.objects.filter(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=EAST_OF_ENGLAND,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
                "old_code"
            ],
        ).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=NORTH_WEST,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()

        # When
        self.migrate_forward()

        # Then
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        APITimeSeries = self.get_model("apitimeseries")
        # Check that the `Geography` records have been updated as per the new names and geography codes
        assert not Geography.objects.filter(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert Geography.objects.filter(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["new_code"],
        ).exists()
        assert not Geography.objects.filter(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"],
        ).exists()

        # Check all dependencies no longer reference the old geography codes
        assert not CoreTimeSeries.objects.filter(
            geography__name=EAST_OF_ENGLAND,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
                "old_code"
            ],
        ).exists()
        assert not CoreTimeSeries.objects.filter(
            geography__name=NORTH_WEST,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert not APITimeSeries.objects.filter(
            geography=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert not APITimeSeries.objects.filter(
            geography=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()

        # Check all dependencies reference the new geography codes
        assert CoreTimeSeries.objects.filter(
            geography__name=EAST_OF_ENGLAND,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
                "new_code"
            ],
        ).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=NORTH_WEST,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["new_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"],
        ).exists()

        # When
        self.migrate_backward()

        # Then
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        APITimeSeries = self.get_model("apitimeseries")

        # Check that the existing records are as per the original names
        assert Geography.objects.filter(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=EAST_OF_ENGLAND,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
                "old_code"
            ],
        ).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=NORTH_WEST,
            geography__geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
        ).exists()
        assert APITimeSeries.objects.filter(
            geography=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
        ).exists()

    def _create_all_pre_existing_models(self):
        east_of_england, north_west = self._create_pre_existing_geographies()
        self._create_pre_existing_core_models(
            east_of_england=east_of_england, north_west=north_west
        )
        self._create_pre_existing_api_models()

    def _create_pre_existing_geographies(self):
        Geography = self.get_model("geography")
        GeographyType = self.get_model("geographytype")

        nhs_trust = GeographyType.objects.create(name="NHS Region")
        east_of_england = Geography.objects.create(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
            geography_type=nhs_trust,
        )

        north_west = Geography.objects.create(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
            geography_type=nhs_trust,
        )

        return east_of_england, north_west

    def _create_pre_existing_core_models(self, *, east_of_england, north_west):
        CoreTimeSeries = self.get_model("coretimeseries")
        Stratum = self.get_model("stratum")
        stratum = Stratum.objects.create(name="default")
        Age = self.get_model("age")
        age = Age.objects.create(name="all")
        datetime_for_records = datetime.datetime(year=2024, month=1, day=1)

        Metric = self.get_model("metric")
        metric = Metric.objects.create(name="COVID-19_healthcare_occupiedBedsByDay")

        east_of_england_time_series = CoreTimeSeries.objects.create(
            stratum=stratum,
            age=age,
            metric=metric,
            refresh_date=datetime_for_records,
            geography=east_of_england,
            date=datetime_for_records,
            metric_value=123,
            year=2024,
            epiweek=1,
        )
        north_west_time_series = CoreTimeSeries.objects.create(
            stratum=stratum,
            age=age,
            metric=metric,
            refresh_date=datetime_for_records,
            geography=north_west,
            date=datetime_for_records,
            metric_value=456,
            year=2024,
            epiweek=1,
        )
        return east_of_england_time_series, north_west_time_series

    def _create_pre_existing_api_models(self):
        APITimeSeries = self.get_model("apitimeseries")
        current_datetime = datetime.datetime.now()

        north_west_time_series = APITimeSeries.objects.create(
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
            geography_type=NHS_REGION,
            geography=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
            metric="COVID-19_healthcare_occupiedBedsByDay",
            stratum="default",
            sex="all",
            metric_value=123,
            metric_group="healthcare",
            year=2024,
            epiweek=1,
            date=current_datetime,
            refresh_date=current_datetime,
        )
        east_of_england_time_series = APITimeSeries.objects.create(
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
            geography_type=NHS_REGION,
            geography=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
            metric="COVID-19_healthcare_occupiedBedsByDay",
            stratum="default",
            sex="all",
            metric_value=456,
            metric_group="healthcare",
            year=2024,
            epiweek=1,
            date=current_datetime,
            refresh_date=current_datetime,
        )
        return north_west_time_series, east_of_england_time_series
