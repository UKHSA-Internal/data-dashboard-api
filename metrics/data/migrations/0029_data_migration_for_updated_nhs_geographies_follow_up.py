import logging

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

MIDLANDS = "Midlands"
NORTH_EAST = "North East and Yorkshire"

NHS_REGIONS_UPDATE_LOOKUP = {
    MIDLANDS: {"old_code": "E40000008", "new_code": "E40000011"},
    NORTH_EAST: {"old_code": "E40000009", "new_code": "E40000012"},
}

NHS_TRUST_UPDATE_LOOKUP = {
    "old_name": "St Helens and Knowsley Teaching Hospitals NHS Trust",
    "new_name": "Mersey and West Lancashire Teaching Hospitals NHS Trust",
}

logger = logging.getLogger(__name__)


def migrate_api_timeseries_forwards(*, apps: StateApps):
    APITimeSeries = apps.get_model("data", "APITimeSeries")
    logger.info("Migrating geography code of all `APITimeSeries` Midlands records")
    midlands_api_time_series = APITimeSeries.objects.filter(
        geography=MIDLANDS,
        geography_type="NHS Region",
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["old_code"],
    )
    midlands_api_time_series.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["new_code"]
    )

    logger.info(
        "Migrating geography code of all `APITimeSeries` North East and Yorkshire records"
    )
    north_east_api_time_series = APITimeSeries.objects.filter(
        geography=NORTH_EAST,
        geography_type="NHS Region",
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["old_code"],
    )
    north_east_api_time_series.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["new_code"]
    )

    logger.info(
        "Migrating all `APITimeSeries` records from St Helens to Mersey and West Lancashire Trust"
    )
    st_helens_api_time_series = APITimeSeries.objects.filter(
        geography=NHS_TRUST_UPDATE_LOOKUP["old_name"],
        geography_type="NHS Trust",
        geography_code="RBN",
    )
    st_helens_api_time_series.update(geography=NHS_TRUST_UPDATE_LOOKUP["new_name"], force_write=True)


def migrate_api_timeseries_backwards(*, apps: StateApps):
    APITimeSeries = apps.get_model("data", "APITimeSeries")
    logger.info("Reverting geography code of all `APITimeSeries` Midlands records")
    midlands_api_time_series = APITimeSeries.objects.filter(
        geography=MIDLANDS,
        geography_type="NHS Region",
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["new_code"],
    )
    midlands_api_time_series.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["old_code"]
    )

    logger.info(
        "Reverting geography code of all `APITimeSeries` North East and Yorkshire records"
    )
    north_east_api_time_series = APITimeSeries.objects.filter(
        geography=NORTH_EAST,
        geography_type="NHS Region",
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["new_code"],
    )
    north_east_api_time_series.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["old_code"]
    )

    logger.info(
        "Reverting all `APITimeSeries` records from Mersey and West Lancashire Trust to St Helens"
    )
    mersey_api_time_series = APITimeSeries.objects.filter(
        geography=NHS_TRUST_UPDATE_LOOKUP["new_name"],
        geography_type="NHS Trust",
        geography_code="RBN",
    )
    mersey_api_time_series.update(geography=NHS_TRUST_UPDATE_LOOKUP["old_name"])


def migrate_st_helens_core_models_forwards(*, apps: StateApps):
    GeographyType = apps.get_model("data", "GeographyType")
    try:
        nhs_trust = GeographyType.objects.get(name="NHS Trust")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Trust `GeographyType` not found, can't migrate associated `Geography` records"
        )
        return

    Geography = apps.get_model("data", "Geography")
    try:
        st_helens_trust = Geography.objects.get(
            name=NHS_TRUST_UPDATE_LOOKUP["old_name"],
            geography_code="RBN",
            geography_type=nhs_trust,
        )
    except Geography.DoesNotExist:
        logger.info(
            "St Helens and Knowsley `Geography` not found, no need to update associated records"
        )
        return

    try:
        mersey_trust = Geography.objects.get(
            name=NHS_TRUST_UPDATE_LOOKUP["new_name"],
            geography_code="RBN",
            geography_type=nhs_trust,
        )
    except Geography.DoesNotExist:
        logger.info(
            "Mersey and West Lancashire Trust `Geography` not found, can't update the associated records"
        )
        return

    CoreTimeSeries = apps.get_model("data", "CoreTimeSeries")
    logger.info(
        "Migrating all `CoreTimeSeries` records from St Helens to Mersey and West Lancashire Trust"
    )
    st_helens_core_time_series = CoreTimeSeries.objects.filter(
        geography_id=st_helens_trust.id
    )
    st_helens_core_time_series.update(geography_id=mersey_trust.id, force_write=True)

    logger.info(
        "Migrating all `CoreHeadline` records from St Helens to Mersey and West Lancashire Trust"
    )
    CoreHeadline = apps.get_model("data", "CoreHeadline")
    st_helens_core_headline = CoreHeadline.objects.filter(
        geography_id=st_helens_trust.id
    )
    st_helens_core_headline.update(geography_id=mersey_trust.id, force_write=True)

    st_helens_trust.delete()


def migrate_mersey_core_models_backwards(*, apps: StateApps):
    GeographyType = apps.get_model("data", "GeographyType")
    try:
        nhs_trust = GeographyType.objects.get(name="NHS Trust")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Trust `GeographyType` not found, can't migrate associated `Geography` records"
        )
        return

    Geography = apps.get_model("data", "Geography")
    try:
        mersey_trust = Geography.objects.get(
            name=NHS_TRUST_UPDATE_LOOKUP["new_name"],
            geography_code="RBN",
            geography_type=nhs_trust,
        )
    except Geography.DoesNotExist:
        logger.info(
            "Mersey and West Lancashire Trust `Geography` not found, no need to revert the associated records"
        )
        return

    st_helens_trust, _ = Geography.objects.get_or_create(
        name=NHS_TRUST_UPDATE_LOOKUP["old_name"],
        geography_code="RBN",
        geography_type=nhs_trust,
    )

    CoreTimeSeries = apps.get_model("data", "CoreTimeSeries")
    logger.info(
        "Reverting all `CoreTimeSeries` records from Mersey and West Lancashire Trust to St Helens"
    )
    mersey_core_time_series = CoreTimeSeries.objects.filter(
        geography_id=mersey_trust.id
    )
    mersey_core_time_series.update(geography_id=st_helens_trust.id)

    logger.info(
        "Migrating all `CoreHeadline` records from Mersey and West Lancashire Trust to St Helens"
    )
    CoreHeadline = apps.get_model("data", "CoreHeadline")
    mersey_core_headline = CoreHeadline.objects.filter(geography_id=mersey_trust.id)
    mersey_core_headline.update(geography_id=st_helens_trust.id)


def forwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    migrate_api_timeseries_forwards(apps=apps)
    migrate_st_helens_core_models_forwards(apps=apps)


def backwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    migrate_api_timeseries_backwards(apps=apps)
    migrate_mersey_core_models_backwards(apps=apps)


class Migration(migrations.Migration):
    dependencies = [
        (
            "data",
            "0028_data_migration_for_updated_nhs_geographies",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_migration,
            reverse_code=backwards_migration,
        )
    ]
