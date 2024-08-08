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


def forwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    GeographyType = apps.get_model("data", "GeographyType")
    try:
        GeographyType.objects.get(name="NHS Region")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Region `GeographyType` not found, can't update associated `Geography` records"
        )
    else:
        _update_nhs_regions(apps=apps)

    try:
        GeographyType.objects.get(name="NHS Trust")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Trust `GeographyType` not found, can't update associated `Geography` records"
        )
        return
    else:
        _update_nhs_trust(apps=apps)


def _update_nhs_regions(*, apps: StateApps):
    Geography = apps.get_model("data", "Geography")
    GeographyType = apps.get_model("data", "GeographyType")
    nhs_region = GeographyType.objects.get(name="NHS Region")

    try:
        midlands = Geography.objects.get(
            name=MIDLANDS,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["old_code"],
            geography_type=nhs_region,
        )
    except Geography.DoesNotExist:
        logger.info(
            "Midlands `Geography` not found, can't update the associated `geography_code`"
        )
    else:
        midlands.geography_code = NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["new_code"]
        midlands.save()

    try:
        north_east_and_yorkshire = Geography.objects.get(
            name=NORTH_EAST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["old_code"],
            geography_type=nhs_region,
        )
    except Geography.DoesNotExist:
        logger.info(
            "North East and Yorkshire `Geography` not found, can't update the associated `geography_code`"
        )
        return
    north_east_and_yorkshire.geography_code = NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST][
        "new_code"
    ]
    north_east_and_yorkshire.save()


def _update_nhs_trust(*, apps: StateApps) -> None:
    Geography = apps.get_model("data", "Geography")
    GeographyType = apps.get_model("data", "GeographyType")
    nhs_trust = GeographyType.objects.get(name="NHS Trust")

    try:
        st_helens_trust = Geography.objects.get(
            name=NHS_TRUST_UPDATE_LOOKUP["old_name"],
            geography_code="RBN",
            geography_type=nhs_trust,
        )
    except Geography.DoesNotExist:
        logger.info(
            "St Helens and Knowsley `Geography` not found, can't update the associated `name`"
        )
        return

    if Geography.objects.filter(name=NHS_TRUST_UPDATE_LOOKUP["new_name"]).exists():
        logger.info(
            "Mersey and West Lancashire Teaching Hospitals NHS Trust `Geography` already exists. "
            "Must migrate dependencies of St Helens seperately."
        )
        return

    st_helens_trust.name = NHS_TRUST_UPDATE_LOOKUP["new_name"]
    st_helens_trust.save()


def backwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    GeographyType = apps.get_model("data", "GeographyType")
    try:
        GeographyType.objects.get(name="NHS Region")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Region `GeographyType` not found, can't revert associated `Geography` records"
        )
    else:
        _revert_updates_to_nhs_regions(apps=apps)

    try:
        GeographyType.objects.get(name="NHS Trust")
    except GeographyType.DoesNotExist:
        logger.info(
            "NHS Trust `GeographyType` not found, can't revert associated `Geography` records"
        )
        return
    else:
        _revert_updates_to_nhs_trust(apps=apps)


def _revert_updates_to_nhs_regions(*, apps: StateApps):
    GeographyType = apps.get_model("data", "GeographyType")
    nhs_region = GeographyType.objects.get(name="NHS Region")

    Geography = apps.get_model("data", "Geography")
    try:
        midlands = Geography.objects.get(
            name=MIDLANDS,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["new_code"],
            geography_type=nhs_region,
        )
    except Geography.DoesNotExist:
        logger.info(
            "Midlands `Geography` not found, can't revert the associated `geography_code`"
        )
    else:
        midlands.geography_code = NHS_REGIONS_UPDATE_LOOKUP[MIDLANDS]["old_code"]
        midlands.save()

    try:
        north_east_and_yorkshire = Geography.objects.get(
            name=NORTH_EAST,
            geography_code=NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST]["new_code"],
            geography_type=nhs_region,
        )
    except Geography.DoesNotExist:
        logger.info(
            "North East and Yorkshire `Geography` not found, can't revert the associated `geography_code`"
        )
        return
    else:
        north_east_and_yorkshire.geography_code = NHS_REGIONS_UPDATE_LOOKUP[NORTH_EAST][
            "old_code"
        ]
        north_east_and_yorkshire.save()


def _revert_updates_to_nhs_trust(*, apps: StateApps) -> None:
    GeographyType = apps.get_model("data", "GeographyType")
    nhs_trust = GeographyType.objects.get(name="NHS Trust")

    Geography = apps.get_model("data", "Geography")
    try:
        mersey_and_west_lancashire_trust = Geography.objects.get(
            name=NHS_TRUST_UPDATE_LOOKUP["new_name"],
            geography_code="RBN",
            geography_type=nhs_trust,
        )
    except Geography.DoesNotExist:
        logger.info(
            "Mersey and West Lancashire `Geography` not found, can't revert the associated `name`"
        )
        return

    mersey_and_west_lancashire_trust.name = NHS_TRUST_UPDATE_LOOKUP["old_name"]
    mersey_and_west_lancashire_trust.save()


class Migration(migrations.Migration):

    dependencies = [
        (
            "data",
            "0027_add_force_write_flag_to_bypass_uniqe_constraints_for_timeseries",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_migration,
            reverse_code=backwards_migration,
        )
    ]
