import pytest

from tests.migrations.helper import MigrationTests


@pytest.mark.django_db(transaction=True)
class Test0002DownloadButtonSnippet(MigrationTests):
    previous_migration_name = "0001_initial"
    current_migration_name = "0002_download_button_snippet"
    current_django_app = "snippets"

    def test_forward_and_then_backward_migration(self):
        """
        Given the database contains no button snippets.
        When the new migration is applied.
        Then the `Button` record is created for download button.
        When the migration is rolled back.
        Then the `Button` record for download button is removed.
        """
        # Given
        self.migrate_backward()

        download_button = self.get_model("button")
        assert not download_button.objects.exists()

        # When
        self.migrate_forward()

        # Then
        download_button = self.get_model("button")
        assert download_button.objects.count() == 1

        # When
        self.migrate_backward()

        # Then
        download_button = self.get_model("button")
        assert not download_button.objects.exists()
        self.migrate_forward()
