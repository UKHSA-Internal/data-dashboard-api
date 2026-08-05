from django.db import migrations
from cms.utils.migrations.backfill_helpers import backfill_pages_with_theme_and_subtheme


def backfill_topic_pages(apps, schema_editor):
    backfill_pages_with_theme_and_subtheme(apps, "topic", "TopicPage")


def noop(apps, schema_editor):
    """Backfill is one-directional; nothing sensible to reverse."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("topic", "0036_alter_topicpage_body"),
    ]
    operations = [
        migrations.RunPython(backfill_topic_pages, noop),
    ]