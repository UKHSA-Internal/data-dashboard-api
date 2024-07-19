import pytest

from tests.migrations.helper import MigrationTests

MIDLANDS = "Midlands"
NORTH_EAST_AND_YORKSHIRE = "North East and Yorkshire"
ST_HELENS_NHS_TRUST = "St Helens and Knowsley Teaching Hospitals NHS Trust"
MERSEY_NHS_TRUST = "Mersey and West Lancashire Teaching Hospitals NHS Trust"


@pytest.mark.django_db(transaction=True)
class Test0027DataMigrationForUpdatedNHSGeographies(MigrationTests):
    previous_migration_name = (
        "0026_rename_in_reporting_lag_period_to_in_reporting_delay_period"
    )
    current_migration_name = "0027_data_migration_for_updated_nhs_geographies"
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
        self._create_pre_existing_geographies()
        Geography = self.get_model("geography")

        # Check that the existing `Geography` records are as per the original names and geography codes
        assert Geography.objects.filter(
            name=MIDLANDS, geography_code="E40000008"
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_EAST_AND_YORKSHIRE, geography_code="E40000009"
        ).exists()
        assert Geography.objects.filter(name=ST_HELENS_NHS_TRUST).exists()

        # When
        self.migrate_forward()

        # Then
        Geography = self.get_model("geography")
        # Check that the `Geography` records have been updated as per the new names and geography codes
        assert Geography.objects.filter(
            name=MIDLANDS, geography_code="E40000011"
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_EAST_AND_YORKSHIRE, geography_code="E40000012"
        ).exists()

        assert Geography.objects.filter(name=MERSEY_NHS_TRUST).exists()
        assert not Geography.objects.filter(name=ST_HELENS_NHS_TRUST).exists()

        # When
        self.migrate_backward()

        # Then
        Geography = self.get_model("geography")
        # Check that the `Geography` records have been revered as per the original names and geography codes
        assert Geography.objects.filter(
            name=MIDLANDS, geography_code="E40000008"
        ).exists()
        assert Geography.objects.filter(
            name=NORTH_EAST_AND_YORKSHIRE, geography_code="E40000009"
        ).exists()
        assert Geography.objects.filter(name=ST_HELENS_NHS_TRUST).exists()

    def _create_pre_existing_geographies(self):
        Geography = self.get_model("geography")
        GeographyType = self.get_model("geographytype")

        nhs_region = GeographyType.objects.create(name="NHS Region")
        midlands = Geography.objects.create(
            name="Midlands", geography_code="E40000008", geography_type=nhs_region
        )
        north_east_and_yorkshire = Geography.objects.create(
            name="North East and Yorkshire",
            geography_code="E40000009",
            geography_type=nhs_region,
        )

        nhs_trust = GeographyType.objects.create(name="NHS Trust")
        st_helens_trust = Geography.objects.create(
            name="St Helens and Knowsley Teaching Hospitals NHS Trust",
            geography_code="RBN",
            geography_type=nhs_trust,
        )

        return midlands, north_east_and_yorkshire, st_helens_trust
