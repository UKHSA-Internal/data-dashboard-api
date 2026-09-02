from django.db import migrations
from cms.utils.migrations.backfill_helpers import backfill_pages_with_theme_and_subtheme


def backfill_topics_list_pages(apps, schema_editor):
    backfill_pages_with_theme_and_subtheme(apps, "topics_list", "TopicsListPage")


def noop(apps, schema_editor):
    """Backfill is one-directional; nothing sensible to reverse."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("topics_list", "0011_alter_topicslistpage_body"),
    ]
    operations = [
        migrations.RunPython(backfill_topics_list_pages, noop),
    ]
