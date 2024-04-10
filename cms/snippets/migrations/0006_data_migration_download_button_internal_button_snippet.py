from django.db import migrations

from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_internal_button_snippet,
    remove_internal_button_snippets,
)


class Migration(migrations.Migration):
    dependencies = [
        (
            "snippets",
            "0005_internalbutton_snippet",
        )
    ]

    operations = [
        migrations.RunPython(
            code=get_or_create_download_button_internal_button_snippet,
            reverse_code=remove_internal_button_snippets,
        )
    ]
