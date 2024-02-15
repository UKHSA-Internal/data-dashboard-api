from django.db import migrations

from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_snippet,
    remove_buttons_snippets,
)


class Migration(migrations.Migration):
    dependencies = [
        (
            "snippets",
            "0001_initial",
        )
    ]

    operations = [
        migrations.RunPython(
            code=get_or_create_download_button_snippet,
            reverse_code=remove_buttons_snippets,
        )
    ]
