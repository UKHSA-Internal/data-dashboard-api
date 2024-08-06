import datetime

import pytest

from tests.migrations.helper import MigrationTests

MIDLANDS = "Midlands"
NORTH_EAST_AND_YORKSHIRE = "North East and Yorkshire"
ST_HELENS_NHS_TRUST = "St Helens and Knowsley Teaching Hospitals NHS Trust"
MERSEY_NHS_TRUST = "Mersey and West Lancashire Teaching Hospitals NHS Trust"


@pytest.mark.django_db(transaction=True)
class Test0029DataMigrationForUpdatedNHSGeographiesFollowUp(MigrationTests):
    previous_migration_name = "0028_data_migration_for_updated_nhs_geographies"
    current_migration_name = "0029_data_migration_for_updated_nhs_geographies_follow_up"
    current_django_app = "data"

    def test_forward_and_then_backward_migration(self):
        """
        Given the database contains existing `Geography` records.
        When the new migration is applied
        Then the `Geography` records are updated
        When the migration is rolled back
        Then the changes to the `Geography` records are reverted
        """
        # Given
        self.migrate_backward()
        self._create_all_pre_existing_models()
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        CoreHeadline = self.get_model("coreheadline")
        APITimeSeries = self.get_model("apitimeseries")

        # Check that the existing records are as per the original names
        assert Geography.objects.filter(name=ST_HELENS_NHS_TRUST).exists()
        assert Geography.objects.filter(name=MERSEY_NHS_TRUST).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=ST_HELENS_NHS_TRUST
        ).exists()
        assert CoreHeadline.objects.filter(geography__name=ST_HELENS_NHS_TRUST).exists()
        assert APITimeSeries.objects.filter(geography=ST_HELENS_NHS_TRUST).exists()

        # When
        self.migrate_forward()

        # Then
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        CoreHeadline = self.get_model("coreheadline")
        # Check that the `Geography` records have been updated as per the new names and geography codes
        assert not Geography.objects.filter(
            name=ST_HELENS_NHS_TRUST,
            geography_code="RBN",
            geography_type__name="NHS Trust",
        ).exists()
        assert Geography.objects.filter(
            name=MERSEY_NHS_TRUST,
            geography_code="RBN",
            geography_type__name="NHS Trust",
        ).exists()

        # Check all dependencies no longer reference St Helens
        assert not CoreTimeSeries.objects.filter(
            geography__name=ST_HELENS_NHS_TRUST
        ).exists()
        assert not CoreHeadline.objects.filter(
            geography__name=ST_HELENS_NHS_TRUST
        ).exists()
        assert not APITimeSeries.objects.filter(geography=ST_HELENS_NHS_TRUST).exists()

        # Check all dependencies reference Mersey instead
        assert CoreTimeSeries.objects.filter(geography__name=MERSEY_NHS_TRUST).exists()
        assert CoreHeadline.objects.filter(geography__name=MERSEY_NHS_TRUST).exists()
        assert APITimeSeries.objects.filter(geography=MERSEY_NHS_TRUST).exists()

        # When
        self.migrate_backward()

        # Then
        Geography = self.get_model("geography")
        CoreTimeSeries = self.get_model("coretimeseries")
        CoreHeadline = self.get_model("coreheadline")

        # Check that the existing records are as per the original names
        assert Geography.objects.filter(name=ST_HELENS_NHS_TRUST).exists()
        assert Geography.objects.filter(name=MERSEY_NHS_TRUST).exists()
        assert CoreTimeSeries.objects.filter(
            geography__name=ST_HELENS_NHS_TRUST
        ).exists()
        assert CoreHeadline.objects.filter(geography__name=ST_HELENS_NHS_TRUST).exists()
        assert APITimeSeries.objects.filter(geography=ST_HELENS_NHS_TRUST).exists()

    def _create_all_pre_existing_models(self):
        st_helens, mersey = self._create_pre_existing_geographies()
        self._create_pre_existing_core_models(st_helens=st_helens)
        self._create_pre_existing_api_timeseries()

    def _create_pre_existing_geographies(self):
        Geography = self.get_model("geography")
        GeographyType = self.get_model("geographytype")

        nhs_trust = GeographyType.objects.create(name="NHS Trust")
        mersey_trust = Geography.objects.create(
            name=MERSEY_NHS_TRUST,
            geography_code="RBN",
            geography_type=nhs_trust,
        )

        st_helens_trust = Geography.objects.create(
            name=ST_HELENS_NHS_TRUST,
            geography_code="RBN",
            geography_type=nhs_trust,
        )

        return st_helens_trust, mersey_trust

    def _create_pre_existing_core_models(self, st_helens):
        CoreHeadline = self.get_model("coreheadline")
        CoreTimeSeries = self.get_model("coretimeseries")

        Stratum = self.get_model("stratum")
        stratum = Stratum.objects.create(name="default")
        Age = self.get_model("age")
        age = Age.objects.create(name="all")
        current_datetime = datetime.datetime.now()

        Metric = self.get_model("metric")
        metric = Metric.objects.create(name="COVID-19_healthcare_occupiedBedsByDay")

        core_headline = CoreHeadline.objects.create(
            stratum=stratum,
            age=age,
            metric=metric,
            refresh_date=current_datetime,
            geography=st_helens,
            period_end=current_datetime,
            period_start=current_datetime,
            metric_value=123,
        )
        core_time_series = CoreTimeSeries.objects.create(
            stratum=stratum,
            age=age,
            metric=metric,
            refresh_date=current_datetime,
            geography=st_helens,
            date=current_datetime,
            metric_value=456,
            year=2024,
            epiweek=1,
        )

        return core_headline, core_time_series

    def _create_pre_existing_api_timeseries(self):
        APITimeSeries = self.get_model("apitimeseries")
        current_datetime = datetime.datetime.now()
        APITimeSeries.objects.create(
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
            geography_type="NHS Trust",
            geography=ST_HELENS_NHS_TRUST,
            geography_code="RBN",
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
