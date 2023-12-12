import datetime

from cms.metrics_documentation.models import MetricsDocumentationChildEntry, MetricsDocumentationParentPage
from cms.metrics_documentation.utils import get_metrics_definitions
from cms.home.models import HomePage
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
        date_posted=datetime.datetime.today(),
        page_description="page description single",
        metric="COVID-19_cases_rateRollingMean",
        body=[
            {
                "type": "section",
                "value": {"title": "section title", "body": "section body"},
            }
        ],
    )


def forward_model_creation(*args, **kwargs):
    entries = get_metrics_definitions()
    for entry in entries:
        MetricsDocumentationChildEntry.objects.create(**entry)


def reverse_model_creation(*args, **kwargs):
    MetricsDocumentationChildEntry.objects.all().delete()


def make_parent(*args, **kwargs):

    if MetricsDocumentationParentPage.objects.get_live_pages():
        print("found something")
        return

    MetricsDocumentationParentPage.objects.create(
        title="metrics documentation",
        depth=1,
        # slug="metrics-documentation",
        # seo_title="metrics-documentation",
        date_posted=datetime.datetime.today(),
        body=(
           "<p data-block-key=\"wk1ht\">"
           "Here we outline a list of metrics available in the UKHSA"
           "data dashboard. Click to view more information about a metric"
           "</p>",
        )
    )
    # try:
    #     MetricsDocumentationParentPage.objects.get_live_pages()
    #     print("found something")
    #     return
    # except:
    #     print("creating a new page")
    #     MetricsDocumentationParentPage.objects.create(
    #         title="metrics documentation",
    #         date_posted=datetime.datetime.today(),
    #         body=(
    #            "<p data-block-key=\"wk1ht\">"
    #            "Here we outline a list of metrics available in the UKHSA"
    #            "data dashboard. Click to view more information about a metric"
    #            "</p>",
    #         )
    #     )


class Migration(migrations.Migration):
    dependencies = [("metrics_documentation", "0002_metricsdocumentationchildentry")]

    operations = [
        migrations.RunPython(
            code=make_parent
        ),
        # migrations.RunPython(
        #     code=make_models,
        #     reverse_code=reverse_model_creation,
        # )
    ]
