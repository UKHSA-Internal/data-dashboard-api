import logging

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

logger = logging.getLogger(__name__)


def _change_api_geography(apps: StateApps, geographies, picker):
    APITimeSeries = apps.get_model("data", "APITimeSeries")

    for geography in geographies:
        old, new = picker(geography)
        targets = APITimeSeries.objects.filter(
            geography=old["name"],
            geography_code=old["code"],
        )
        targets.update(
            geography=new["name"],
            geography_code=new["code"],
        )
        logger.info(
            "Migrated %s geography change on %s `APITimeSeries` records of %s total",
            geography,
            targets.count(),
            APITimeSeries.objects.count(),
        )


def update_api_geography(apps: StateApps, geographies):
    _change_api_geography(apps, geographies, lambda x: (x["old"], x["new"]))


def revert_api_geography(apps: StateApps, geographies):
    _change_api_geography(apps, geographies, lambda x: (x["new"], x["old"]))


def _change_core_geography(apps: StateApps, geographies, picker):
    Geography = apps.get_model("data", "Geography")

    for geography in geographies:
        old, new = picker(geography)

        try:
            target = Geography.objects.get(name=old["name"], geography_code=old["code"])
        except Geography.DoesNotExist:
            logger.error(  # noqa: TRY400 - we don't want stack trace
                "`Geography` %s not found on %s Geography records can't update the associated `geography_code`",
                old,
                Geography.objects.count(),
            )
        else:
            target.geography_code = new["code"]
            target.geography_name = new["name"]
            target.save()


def update_core_geography(*, apps: StateApps, geographies):
    _change_core_geography(apps, geographies, lambda x: (x["old"], x["new"]))


def revert_core_geography(*, apps: StateApps, geographies):
    _change_core_geography(apps, geographies, lambda x: (x["new"], x["old"]))


GEOGRAPHIES = [
    {
        "old": {
            "name": "NHS Central East Integrated Care Board",
            "code": "QUE",
            "type": 67,
        },
        "new": {
            "name": "NHS Central East Integrated Care Board",
            "code": "S1Y5D",
            "type": 67,
        },
    },
    {
        "old": {
            "name": "NHS Essex Integrated Care Board",
            "code": "QH8",
            "type": 67,
        },
        "new": {
            "name": "NHS Essex Integrated Care Board",
            "code": "D7T5G",
            "type": 67,
        },
    },
    {
        "old": {
            "name": "NHS Surrey and Sussex Integrated Care Board",
            "code": "QJG",
            "type": 67,
        },
        "new": {
            "name": "NHS Surrey and Sussex Integrated Care Board",
            "code": "S9B9J",
            "type": 67,
        },
    },
    {
        "old": {
            "name": "NHS Thames Valley Integrated Care Board",
            "code": "QU9",
            "type": 67,
        },
        "new": {
            "name": "NHS Thames Valley Integrated Care Board",
            "code": "S0E4D",
            "type": 67,
        },
    },
    {
        "old": {
            "name": "NHS West and North London Integrated Care Board",
            "code": "QMJ",
            "type": 67,
        },
        "new": {
            "name": "NHS West and North London Integrated Care Board",
            "code": "Z9B2Z",
            "type": 67,
        },
    },
]


def forwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    update_core_geography(apps=apps, geographies=GEOGRAPHIES)
    update_api_geography(apps=apps, geographies=GEOGRAPHIES)


def backwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    revert_core_geography(apps=apps, geographies=GEOGRAPHIES)
    revert_api_geography(apps=apps, geographies=GEOGRAPHIES)


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0043_alter_apitimeseries_metric_value_rename_second_category"),
    ]

    operations = [
        migrations.RunPython(
            code=forwards_migration,
            reverse_code=backwards_migration,
        )
    ]
