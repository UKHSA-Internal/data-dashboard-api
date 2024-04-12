import pytest

from tests.migrations.helper import MigrationTests


@pytest.mark.django_db(transaction=True)
class Test0006DataMigrationDownloadButtonInternalButtonSnippet(MigrationTests):
    previous_migration_name = "0005_internalbutton_snippet"
    current_migration_name = (
        "0006_data_migration_download_button_internal_button_snippet"
    )
    current_django_app = "snippets"

    def test_forward_and_then_backward_migration(self):
        """
        Given the database contains no internal button snippets.
        When the new migration is applied.
        Then the `InternalButton` record is created for download button.
        When the migration is rolled back.
        Then the `InternalButton` record for download button is removed.
        """
        # Given
        self.migrate_backward()

        download_button = self.get_model("internalbutton")
        assert not download_button.objects.exists()

        # When
        self.migrate_forward()

        # Then
        download_button = self.get_model("internalbutton")
        assert download_button.objects.count() == 1

        # When
        self.migrate_backward()

        # Then
        download_button = self.get_model("internalbutton")
        assert not download_button.objects.exists()
