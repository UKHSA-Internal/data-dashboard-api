from cms.home.models import HomePage
from django.core.management import call_command
import pytest

from tests.migrations.helper import MigrationTests


@pytest.mark.django_db(transaction=True)
class Test0003MetricsDocumentationChildEntriesData(MigrationTests):
    previous_migration_name = "0002_metricsdocumentationchildentry"
    current_migration_name = "0003_metrics_documentation_child_entries_data"
    current_django_app = "metrics_documentation"

    @property
    def metrics_documentation_child_entry(self) -> str:
        return "MetricsDocumentationChildEntry"

    @property
    def metrics_documentation_parent_page(self) -> str:
        return "MetricsDocumentationParentPage"

    def test_forward_and_then_backward_migration(self, dashboard_root_page: HomePage):
        """
        Given the database contains a full set of metrics data
        And no existing `MetricsDocumentationChildEntry`
            or `MetricsDocumentationParentPage` records
        When the new migration is applied
        Then the `MetricsDocumentationChildEntry`
            & `MetricsDocumentationParentPage` records are created
        When the new migration is rolled back
        Then the `MetricsDocumentationChildEntry`
            & `MetricsDocumentationParentPage` records are deleted
        """
        # Given
        self.migrate_backward()

        # Populate the db with metrics data.
        # As the `MetricsDocumentationChildEntry` models will be verified with `Metric` and `Topic` models
        call_command(
            command_name="upload_truncated_test_data", multiprocessing_enabled=False
        )

        # Verify that no `MetricsDocumentationParentPage` models currently exist
        metrics_documentation_parent_page = self.get_model(
            self.metrics_documentation_parent_page
        )
        assert not metrics_documentation_parent_page.objects.exists()

        # Verify that no `MetricsDocumentationChildEntry` models currently exist
        metrics_documentation_child_entry = self.get_model(
            self.metrics_documentation_child_entry
        )
        assert not metrics_documentation_child_entry.objects.exists()

        # When
        self.migrate_forward()

        # Then
        # Verify that the `MetricsDocumentationParentPage` model was populated as expected
        metrics_documentation_parent_page = self.get_model(
            self.metrics_documentation_parent_page
        )
        assert metrics_documentation_parent_page.objects.count() == 1

        # Verify that the `MetricsDocumentationChildEntry` models were populated as expected
        metrics_documentation_child_entry = self.get_model(
            self.metrics_documentation_child_entry
        )
        assert metrics_documentation_child_entry.objects.count() == 55

        # When
        self.migrate_backward()

        # Then
        # Verify that the `MetricsDocumentationParentPage` model is reverted
        metrics_documentation_parent_page = self.get_model(
            self.metrics_documentation_parent_page
        )
        assert not metrics_documentation_parent_page.objects.exists()

        # Verify that all the `MetricsDocumentationChildEntry` models
        # which were created by the latest migration were reverted
        metrics_documentation_child_entry = self.get_model(
            self.metrics_documentation_child_entry
        )
        assert not metrics_documentation_child_entry.objects.exists()
