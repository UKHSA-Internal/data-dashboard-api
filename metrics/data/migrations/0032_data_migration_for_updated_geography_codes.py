import logging

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

EAST_OF_ENGLAND = "East of England"
NORTH_WEST = "North West"
NHS_REGION = "NHS Region"

NHS_REGIONS_UPDATE_LOOKUP = {
    EAST_OF_ENGLAND: {"old_code": "E40000007", "new_code": "E40000013"},
    NORTH_WEST: {"old_code": "E40000010", "new_code": "E40000014"},
}

logger = logging.getLogger(__name__)


def forwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    _update_nhs_regions_for_core_models(apps=apps)
    _update_nhs_regions_for_api_models(apps=apps)


def backwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    _revert_updates_to_nhs_regions_for_core_models(apps=apps)
    _revert_updates_to_nhs_regions_for_api_models(apps=apps)


def _update_nhs_regions_for_api_models(*, apps: StateApps):
    APITimeSeries = apps.get_model("data", "APITimeSeries")

    east_of_england = APITimeSeries.objects.filter(
        geography=EAST_OF_ENGLAND,
        geography_type=NHS_REGION,
    )
    east_of_england.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["new_code"]
    )
    logger.info(
        "Migrated geography code of all possible `APITimeSeries` East of England NHS Region records"
    )

    north_west = APITimeSeries.objects.filter(
        geography=NORTH_WEST,
        geography_type=NHS_REGION,
    )
    north_west.update(geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"])
    logger.info(
        "Migrated geography code of all possible `APITimeSeries` North West NHS Region records"
    )


def _update_nhs_regions_for_core_models(*, apps: StateApps):
    Geography = apps.get_model("data", "Geography")

    try:
        east_of_england = Geography.objects.get(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"],
            geography_type__name=NHS_REGION,
        )
    except Geography.DoesNotExist:
        logger.info(
            "East of England `Geography` not found, can't update the associated `geography_code`"
        )
    else:
        east_of_england.geography_code = NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
            "new_code"
        ]
        east_of_england.save()

    try:
        north_west = Geography.objects.get(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"],
            geography_type__name=NHS_REGION,
        )
    except Geography.DoesNotExist:
        logger.info(
            "North West `Geography` not found, can't update the associated `geography_code`"
        )
        return
    north_west.geography_code = NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"]
    north_west.save()


def _revert_updates_to_nhs_regions_for_core_models(*, apps: StateApps):
    Geography = apps.get_model("data", "Geography")

    try:
        east_of_england = Geography.objects.get(
            name=EAST_OF_ENGLAND,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["new_code"],
            geography_type__name=NHS_REGION,
        )
    except Geography.DoesNotExist:
        logger.info(
            "East of England `Geography` not found, can't update the associated `geography_code`"
        )
    else:
        east_of_england.geography_code = NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND][
            "old_code"
        ]
        east_of_england.save()

    try:
        north_west = Geography.objects.get(
            name=NORTH_WEST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["new_code"],
            geography_type__name=NHS_REGION,
        )
    except Geography.DoesNotExist:
        logger.info(
            "North West `Geography` not found, can't update the associated `geography_code`"
        )
        return
    north_west.geography_code = NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"]
    north_west.save()


def _revert_updates_to_nhs_regions_for_api_models(*, apps: StateApps):
    APITimeSeries = apps.get_model("data", "APITimeSeries")

    east_of_england = APITimeSeries.objects.filter(
        geography=EAST_OF_ENGLAND,
        geography_type=NHS_REGION,
    )
    east_of_england.update(
        geography_code=NHS_REGIONS_UPDATE_LOOKUP[EAST_OF_ENGLAND]["old_code"]
    )
    logger.info(
        "Reverted geography code of all `APITimeSeries` East of England NHS Region records"
    )

    north_west = APITimeSeries.objects.filter(
        geography=NORTH_WEST,
        geography_type=NHS_REGION,
    )
    north_west.update(geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_WEST]["old_code"])
    logger.info(
        "Reverted geography code of all `APITimeSeries` North West NHS Region records"
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "data",
            "0031_add_composite_index_for_api_timeseries",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_migration,
            reverse_code=backwards_migration,
        )
    ]
