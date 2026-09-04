import logging

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

from metrics.utils.geography_update import (
    update_core_geography,
    update_api_geography,
    revert_core_geography,
    revert_api_geography,
)

logger = logging.getLogger(__name__)

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
