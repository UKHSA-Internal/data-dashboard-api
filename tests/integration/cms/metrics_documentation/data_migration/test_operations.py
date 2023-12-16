import datetime

import pytest

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.operations import (
    get_or_create_metrics_documentation_parent_page,
    remove_metrics_documentation_child_entries,
    remove_metrics_documentation_parent_page,
)
from cms.metrics_documentation.models import (
    MetricsDocumentationChildEntry,
    MetricsDocumentationParentPage,
)
from metrics.data.models.core_models import Metric, Topic


class TestRemoveMetricsDocumentationChildEntries:
    @pytest.mark.django_db
    def test_removes_all_child_entries(self):
        """
        Given an existing `MetricsDocumentationChildEntry` model in the database
        When `remove_metrics_documentation_child_entries()` is called
        Then all `MetricsDocumentationChildEntry` models are removed
        """
        # Given
        topic = Topic.objects.create(name="Influenza")
        metric = Metric.objects.create(
            name="influenza_headline_positivityLatest", topic=topic
        )
        MetricsDocumentationChildEntry.objects.create(
            path="abc",
            depth=1,
            title="Test",
            slug="test",
            date_posted=datetime.date.today(),
            page_description="xyz",
            metric=metric.name,
        )
        assert MetricsDocumentationChildEntry.objects.exists()

        # When
        remove_metrics_documentation_child_entries()

        # Then
        assert not MetricsDocumentationChildEntry.objects.exists()


class TestRemoveMetricsDocumentationParentPage:
    @pytest.mark.django_db
    def test_removes_existing_parent_page(self):
        """
        Given an existing `MetricsDocumentationParentPage`
            model in the database
        When `remove_metrics_documentation_parent_page()` is called
        Then all `MetricsDocumentationParentPage` models are removed
        """
        # Given
        MetricsDocumentationParentPage.objects.create(
            path="abc",
            depth=3,
            title="Test",
            slug="metrics-documentation",
            date_posted=datetime.date.today(),
            body="xyz",
        )
        assert MetricsDocumentationParentPage.objects.exists()

        # When
        remove_metrics_documentation_parent_page()

        # Then
        assert not MetricsDocumentationParentPage.objects.exists()


