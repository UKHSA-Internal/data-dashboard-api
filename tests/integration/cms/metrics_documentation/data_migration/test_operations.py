import pytest
from unittest import mock

from cms.home.models import UKHSARootPage
from cms.metrics_documentation.data_migration.child_entries import (
    get_metrics_definitions,
)
from cms.metrics_documentation.data_migration.operations import (
    add_page_as_subpage_to_parent,
    create_metrics_documentation_parent_page_and_child_entries,
    get_or_create_metrics_documentation_parent_page,
    remove_metrics_documentation_child_entries,
    remove_metrics_documentation_parent_page,
)
from cms.metrics_documentation.models import (
    MetricsDocumentationChildEntry,
    MetricsDocumentationParentPage,
)
from ingestion.file_ingestion import _upload_data_as_file
from ingestion.operations.truncated_dataset import (
    _gather_test_data_source_file_paths,
    clear_metrics_tables,
)
from metrics.data.models.core_models import Metric, Topic
from validation.is_public import NON_PUBLIC_DATA_PREFIX


def _seed_truncated_test_data_with_split_auth() -> None:
    """Ingests OFF-SENS files with auth enabled and other files with auth disabled."""
    clear_metrics_tables()

    source_file_paths = _gather_test_data_source_file_paths()
    non_public_file_paths = [
        filepath
        for filepath in source_file_paths
        if filepath.name.startswith(NON_PUBLIC_DATA_PREFIX)
    ]
    public_file_paths = [
        filepath
        for filepath in source_file_paths
        if not filepath.name.startswith(NON_PUBLIC_DATA_PREFIX)
    ]

    with (mock.patch("metrics.api.settings.auth.AUTH_ENABLED", True),):
        for filepath in non_public_file_paths:
            _upload_data_as_file(filepath=filepath)

    with (mock.patch("metrics.api.settings.auth.AUTH_ENABLED", False),):
        for filepath in public_file_paths:
            _upload_data_as_file(filepath=filepath)


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
            theme="test",
            sub_theme="test",
            slug="test",
            page_description="xyz",
            metric=metric.pk,
            topic=metric.topic,
            seo_title="Test",
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
            body="xyz",
            seo_title="Metrics documentation",
        )
        assert MetricsDocumentationParentPage.objects.exists()

        # When
        remove_metrics_documentation_parent_page()

        # Then
        assert not MetricsDocumentationParentPage.objects.exists()


class TestGetOrCreateMetricsDocumentationParentPage:
    @pytest.mark.django_db
    def test_creates_parent_page_if_not_readily_available(
        self, dashboard_root_page: UKHSARootPage
    ):
        """
        Given an existing `UKHSARootPage` record for the root page
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
        assert not parent_page.show_in_menus


class TestCreateMetricsDocumentationParentPageAndChildEntries:
    @pytest.mark.django_db
    def test_creates_correct_child_entries(self, dashboard_root_page: UKHSARootPage):
        """
        Given a number of existing `Topic` and `Metric` combinations
        When `create_metrics_documentation_parent_page_and_child_entries()` is called
        Then the correct child entries are created
            for the corresponding `Metric` records
        """

        # Given

        entries = get_metrics_definitions()
        assert entries, "No metric definitions found"

        test_entry = entries[0]

        topic = Topic.objects.create(name=test_entry["topic"])

        metric = Metric.objects.create(
            id=test_entry["metric"],  # ✅ critical fix
            name=f"metric-{test_entry['metric']}",
            topic=topic,
        )

        # When
        create_metrics_documentation_parent_page_and_child_entries()

        # Then

        child_entry = MetricsDocumentationChildEntry.objects.get(metric=metric.pk)

        expected_title = test_entry["title"]

        assert child_entry.title == expected_title
        assert child_entry.slug == expected_title.lower().replace(" ", "-")
        assert child_entry.topic == test_entry["topic"]
        assert child_entry.seo_title == test_entry["seo_title"]

        assert (
            child_entry.search_description
            == child_entry.page_description
            == test_entry["page_description"]
        )

    @pytest.mark.django_db
    def test_existing_child_entries_are_removed_correctly(
        self, dashboard_root_page: UKHSARootPage
    ):
        """
        Given an existing `MetricsDocumentationParentPage`
        And a related `MetricsDocumentationChildEntry` record
        When `create_metrics_documentation_parent_page_and_child_entries()`
            is called
        Then the pre-existing `MetricsDocumentationChildEntry` record
            is removed accordingly
        And the existing `MetricsDocumentationParentPage` was retained
        """
        # Given
        _seed_truncated_test_data_with_split_auth()
        individual_metric_data = get_metrics_definitions()[0]
        parent_page: MetricsDocumentationParentPage = (
            get_or_create_metrics_documentation_parent_page()
        )
        child_entry = MetricsDocumentationChildEntry(**individual_metric_data)

        add_page_as_subpage_to_parent(subpage=child_entry, parent_page=parent_page)

        # When
        create_metrics_documentation_parent_page_and_child_entries()

        # Then
        assert MetricsDocumentationChildEntry.objects.count() == 55
        assert child_entry not in MetricsDocumentationChildEntry.objects.all()

        assert parent_page in MetricsDocumentationParentPage.objects.all()
