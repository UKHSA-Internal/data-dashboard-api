import logging

from django.db import migrations, models
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps

NHS_TRUST_UPDATE_LOOKUP = {
    "old_name": "St Helens and Knowsley Teaching Hospitals NHS Trust",
    "new_name": "Mersey and West Lancashire Teaching Hospitals NHS Trust",
}

logger = logging.getLogger(__name__)


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

    logger.info(
        "Migrating all `CoreHeadline` records from Mersey and West Lancashire Trust to St Helens"
    )
    CoreHeadline = apps.get_model("data", "CoreHeadline")
    mersey_core_headline = CoreHeadline.objects.filter(geography_id=mersey_trust.id)
    mersey_core_headline.update(geography_id=st_helens_trust.id)


def forwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    migrate_st_helens_core_models_forwards(apps=apps)


def backwards_migration(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    migrate_mersey_core_models_backwards(apps=apps)


class Migration(migrations.Migration):
    dependencies = [
        (
            "data",
            "0029_data_migration_for_updated_nhs_geographies_follow_up",
        ),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="coreheadline",
            name="The `CoreHeadline` record should be unique",
        ),
        migrations.AddField(
            model_name="coreheadline",
            name="force_write",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="coreheadline",
            constraint=models.UniqueConstraint(
                condition=models.Q(("force_write", False)),
                fields=(
                    "metric",
                    "geography",
                    "stratum",
                    "age",
                    "sex",
                    "period_start",
                    "period_end",
                    "metric_value",
                ),
                name="The `CoreHeadline` record should be unique if `force_write` is False",
            ),
        ),
        migrations.RunPython(
            code=forwards_migration,
            reverse_code=backwards_migration,
        ),
    ]
