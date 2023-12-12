import datetime

from cms.metrics_documentation.models import MetricsDocumentationChildEntry
from cms.metrics_documentation.utils import get_metrics_definitions
from django.db import migrations, models


child_entries = [
    {
        "title": "child entry double first",
        "depth": 1,
        "path": "childentrysingle",
        "date_posted": datetime.datetime.today(),
        "page_description": "page description double first",
        "metric": "COVID-19_cases_rateRollingMean",
        "metric_group": "cases",
        "topic": "COVID-19",
        "body": [
            {
                "type": "section",
                "value": {"title": "section title first", "body": "section body first"},
                "id": "8ddaj-fjlsdkf3-fjlksd3-first",
            }
        ],
    },
    {
        "title": "child entry double second",
        "depth": 1,
        "path": "childentrysecond",
        "date_posted": datetime.datetime.today(),
        "page_description": "page description double second",
        "metric": "COVID-19_cases_rateRollingMean",
        "metric_group": "cases",
        "topic": "COVID-19",
        "body": [
            {
                "type": "section",
                "value": {
                    "title": "section title second",
                    "body": "section body second",
                },
                "id": "8ddaj-fjlsdkf3-fjlksd3-second",
            }
        ],
    },
]


def make_multiple_models(*args, **kwargs):
    for model in child_entries:
        MetricsDocumentationChildEntry.objects.create(
            title=model["title"],
            depth=model["depth"],
            path=model["path"],
            date_posted=model["date_posted"],
            page_description=model["page_description"],
            metric=model["metric"],
            topic=model["topic"],
            metric_group=model["metric_group"],
            body=model["body"],
        )


def create_two_models(apps, schema_editor, *args, **kwargs):
    MetricsDocumentationChildEntry.objects.bulk_create(
        [
            MetricsDocumentationChildEntry(child_entries[0]),
            MetricsDocumentationChildEntry(child_entries[1]),
        ]
    )


def make_models(*args, **kwargs):
    MetricsDocumentationChildEntry.objects.create(
        title="child entry page single",
        depth=1,
        path="abc",
        date_posted=datetime.datetime.today(),
        page_description="page description single",
        metric="COVID-19_cases_rateRollingMean",
        topic="COVID-19",
        metric_group="cases",
        body=[
            {
                "type": "section",
                "value": {"title": "section title", "body": "section body"},
                "id": "8ddaj-fjlsdkf3-fjlksd3-fdslk3",
            }
        ],
    )


def forward_model_creation(*args, **kwargs):
    entries = get_metrics_definitions()
    for entry in entries:
        MetricsDocumentationChildEntry.objects.create(**entry)


def reverse_model_creation(*args, **kwargs):
    MetricsDocumentationChildEntry.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("metrics_documentation", "0002_metricsdocumentationchildentry")]

    operations = [
        migrations.RunPython(
            code=forward_model_creation,
            reverse_code=reverse_model_creation,
        )
    ]
