import datetime

import pytest
from django.core.exceptions import ValidationError

from cms.metrics_documentation.models import MetricsDocumentationChildEntry
from metrics.data.models.core_models import Metric, Topic


class TestMetricsDocumentationChildEntry:
    @pytest.mark.django_db
    def test_metric_is_unique(self):
        """
        Given a metric for an existing `MetricsDocumentationChildEntry` record
        When another record is attempted to be created with the same metric
        Then an `ValidationError` is raised
        """
        # Given
        metric_name = "influenza_headline_positivityLatest"
        Metric.objects.create(name=metric_name)
        Topic.objects.create(name=metric_name.split("_")[0].title())

        _create_metrics_documentation_child_entry(metric_name=metric_name, path="doc_1")

        # When / Then
        with pytest.raises(ValidationError):
            _create_metrics_documentation_child_entry(
                metric_name=metric_name, path="doc_2"
            )


def _create_metrics_documentation_child_entry(
    metric_name: str,
    path: str,
) -> MetricsDocumentationChildEntry:
    MetricsDocumentationChildEntry.objects.create(
        metric=metric_name,
        title=metric_name,
        path=path,
        depth=1,
        slug=metric_name,
        date_posted=datetime.date.today(),
        page_description="xyz",
        seo_title=metric_name.replace("_", "").title(),
    )
