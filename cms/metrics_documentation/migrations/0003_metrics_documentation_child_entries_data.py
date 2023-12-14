from django.db import migrations

from cms.metrics_documentation.data_migration import handlers


def pass_over(*args, **kwargs):
    ...


class Migration(migrations.Migration):
    dependencies = [("metrics_documentation", "0002_metricsdocumentationchildentry")]

    operations = [
        migrations.RunPython(
            code=handlers.forward_migration_metrics_documentation_parent_page,
            reverse_code=pass_over,
        ),
        migrations.RunPython(
            code=handlers.forward_migration_metrics_documentation_child_entries,
            reverse_code=handlers.reverse_migration_metrics_documentation_child_entries,
        ),
    ]
