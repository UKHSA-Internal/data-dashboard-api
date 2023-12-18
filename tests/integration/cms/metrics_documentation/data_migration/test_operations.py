import datetime

import pytest
from django.core.management import call_command

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page_and_child_entries,
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


class TestGetOrCreateMetricsDocumentationParentPage:
    @pytest.mark.django_db
    def test_creates_parent_page_if_not_readily_available(
        self, dashboard_root_page: HomePage
    ):
        """
        Given an existing `HomePage` record for the root page
        And no pre-existing `MetricsDocumentationParentPage`
        When `get_or_create_metrics_documentation_parent_page()` is called
        Then a new `MetricsDocumentationParentPage` is created
        """
        # Given
        root_page = dashboard_root_page
        assert not MetricsDocumentationParentPage.objects.exists()

        # When
        parent_page: MetricsDocumentationParentPage = (
            get_or_create_metrics_documentation_parent_page()
        )

        # Then
        assert parent_page.slug == "metrics-documentation"
        assert parent_page.title == "Metrics Documentation"
        # Check the `MetricsDocumentationParentPage`
        # was added as a child of the base root page
        assert parent_page.is_child_of(node=root_page)
        assert parent_page.show_in_menus


class TestCreateMetricsDocumentationParentPageAndChildEntries:
    @pytest.mark.django_db
    def test_creates_correct_child_entries(self, dashboard_root_page: HomePage):
        """
        Given a number of existing `Topic` and `Metric` combinations
        When `create_metrics_documentation_parent_page_and_child_entries()` is called
        Then the correct child entries are created
            for the corresponding `Metric` records
        """
        # Given
        call_command("upload_truncated_test_data")
        healthcare_admission_metric = Metric.objects.get(
            name="RSV_healthcare_admissionRateByWeek"
        )

        # When
        create_metrics_documentation_parent_page_and_child_entries()

        # Then
        healthcare_admission_rate_child_entry = (
            MetricsDocumentationChildEntry.objects.get(
                metric=healthcare_admission_metric.name
            )
        )

        assert healthcare_admission_rate_child_entry.metric_group == "healthcare"
        expected_title = "RSV healthcare admission rate by week"
        assert (
            healthcare_admission_rate_child_entry.slug
            == expected_title.lower().replace(" ", "-")
        )
        assert healthcare_admission_rate_child_entry.topic == "RSV"
        assert healthcare_admission_rate_child_entry.title == expected_title
        assert (
            healthcare_admission_rate_child_entry.seo_title
            == f"{expected_title} | UKHSA data dashboard"
        )

        expected_page_description = (
            "This metric shows the rate per 100,000 people of the total number of people "
            "with confirmed RSV admitted to hospital "
            "(general admissions plus admissions to ICU and HDU) "
            "in the 7 days up to and including the date shown."
        )
        assert (
            healthcare_admission_rate_child_entry.search_description
            == healthcare_admission_rate_child_entry.page_description
            == expected_page_description
        )
