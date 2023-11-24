# Generated by Django 4.2.7 on 2023-11-24 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0020_add_embargo_to_api_and_core_timeseries_and_headline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="geography",
            name="geography_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="geographies",
                to="data.geographytype",
            ),
        ),
    ]
