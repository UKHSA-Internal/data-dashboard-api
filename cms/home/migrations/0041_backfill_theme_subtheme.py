from django.db import migrations
from cms.utils.migrations.backfill_helpers import backfill_pages_with_theme_and_subtheme


def backfill_landing_pages(apps, schema_editor):
    backfill_pages_with_theme_and_subtheme(apps, "home", "LandingPage")


def noop(apps, schema_editor):
    """Backfill is one-directional; nothing sensible to reverse."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0040_alter_landingpage_body"),
    ]
    operations = [
        migrations.RunPython(backfill_landing_pages, noop),
    ]
