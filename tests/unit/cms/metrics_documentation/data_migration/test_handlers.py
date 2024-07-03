from unittest import mock

from _pytest.logging import LogCaptureFixture
from cms.metrics_documentation.data_migration import handlers


class TestForwardMigrationMetricsDocumentationModels:
    def test_logs_stubbed_migration(self, caplog: LogCaptureFixture):
        """
        Given mocked django objects for the apps and schema editor
        When `forward_migration_metrics_documentation_child_entries()` is called
        Then the correct log is recorded
        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()

        # When
        handlers.forward_migration_metrics_documentation_models(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        expected_log = "This migration has been stubbed out and replaced by the `build_cms_site` management command"
        assert expected_log in caplog.text


class TestReverseMigrationMetricsDocumentationModels:
    def test_logs_stubbed_migration(self, caplog):
        """
        Given mocked django objects for the apps and schema editor
        When `reverse_migration_metrics_documentation_models()` is called
        Then the correct log is recorded
        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()

        # When
        handlers.reverse_migration_metrics_documentation_models(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        expected_log = "This migration has been stubbed out and replaced by the `build_cms_site` management command"
        assert expected_log in caplog.text
