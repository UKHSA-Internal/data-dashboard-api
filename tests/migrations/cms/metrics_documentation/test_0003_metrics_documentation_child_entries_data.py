from cms.home.models import HomePage
from wagtail.models import Page
from django.core.management import call_command

import pytest

from tests.migrations.helper import MigrationTestHelper


class Test0003MetricsDocumentationChildEntriesData(MigrationTestHelper):
    previous_migration_name = "0002_metricsdocumentationchildentry"
    current_migration_name = "0003_metrics_documentation_child_entries_data"
    current_django_app = "metrics_documentation"

    @property
    def metrics_documentation_child_entry(self) -> str:
        return "MetricsDocumentationChildEntry"

    @pytest.mark.django_db(transaction=True)
    def test_forwards_migration(self):
        """
        Given the database contains a full set of metrics data
        And no existing `MetricsDocumentationChildEntry` records
        When the new migration is applied
        Then the `MetricsDocumentationChildEntries` records are created
        """
        # Given
        self.migrate_back()
        # Populate the db with metrics data.
        # As the `MetricsDocumentationChildEntry` models will be verified with `Metric` and `Topic` models
        call_command("upload_truncated_test_data", multiprocessing_enabled=False)
        # The root page is required to be in place
        # for the `MetricsDocumentationParentPage` to be creatable
        self._create_root_page()

        # Verify that no `MetricsDocumentationChildEntry` models currently exist
        metrics_documentation_child_entry = self.get_model(
            self.metrics_documentation_child_entry
        )
        assert not metrics_documentation_child_entry.objects.exists()

        # When
        self.migrate_forward()

        # Then
        # Verify that the `MetricsDocumentationChildEntry` models were populated as expected
        metrics_documentation_child_entry = self.get_model(
            self.metrics_documentation_child_entry
        )
        assert metrics_documentation_child_entry.objects.count() == 55

    @staticmethod
    def _create_root_page() -> HomePage:
        root_page = HomePage(
            title="UKHSA Dashboard Root",
            slug="ukhsa-dashboard-root",
        )

        wagtail_root_page = Page.get_first_root_node()
        root_page = wagtail_root_page.add_child(instance=root_page)
        wagtail_root_page.save_revision().publish()

        root_page.save_revision().publish()
        return root_page
