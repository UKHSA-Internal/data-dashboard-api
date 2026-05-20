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
        created_metric = Metric.objects.create(name=metric_name)
        Topic.objects.create(name=metric_name.split("_")[0].title())

        _create_metrics_documentation_child_entry(
            metric_name=metric_name, metric_id=created_metric.pk, path="doc_1"
        )

        # When / Then
        with pytest.raises(ValidationError):
            _create_metrics_documentation_child_entry(
                metric_name=metric_name, metric_id=created_metric.pk, path="doc_2"
            )


def _create_metrics_documentation_child_entry(
    metric_name: str,
    metric_id: int,
    path: str,
) -> MetricsDocumentationChildEntry:
    MetricsDocumentationChildEntry.objects.create(
        metric=metric_id,
        title=metric_name,
        theme="test",
        sub_theme="test",
        topic=1,
        path=path,
        depth=1,
        slug=metric_name,
        page_description="xyz",
        seo_title=metric_name.replace("_", "").title(),
    )
