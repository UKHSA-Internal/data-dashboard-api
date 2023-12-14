from unittest import mock

from _pytest.logging import LogCaptureFixture

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.handlers import (
    forward_migration_metrics_documentation_child_entries,
    forward_migration_metrics_documentation_parent_page,
    reverse_migration_metrics_documentation_child_entries,
)
from cms.metrics_documentation.models import MetricsDocumentationParentPage

MODULE_PATH = "cms.metrics_documentation.data_migration.handlers"


class TestForwardMigrationMetricsDocumentationParentPage:
    @mock.patch(f"{MODULE_PATH}.create_metrics_documentation_parent_page")
    def test_delegates_call_successfully(
        self, spy_create_metrics_documentation_parent_page: mock.MagicMock
    ):
        """
        Given mocked django objects for the apps and schema editor
        When `forward_migration_metrics_documentation_parent_page()` is called
        Then the call is delegated to `create_metrics_documentation_parent_page()`

        Patches:
            `spy_create_metrics_documentation_parent_page`: For the main assertion

        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()

        # When
        forward_migration_metrics_documentation_parent_page(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        spy_create_metrics_documentation_parent_page.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.create_metrics_documentation_parent_page")
    def test_records_log_when_no_root_page_exists(
        self,
        mocked_create_metrics_documentation_parent_page: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given mocked django objects for the apps and schema editor
        And a `HomePage.DoesNotExist` error which is thrown
            when trying to create the parent page
        When `forward_migration_metrics_documentation_parent_page()` is called
        Then the call is delegated to `create_metrics_documentation_parent_page()`

        Patches:
            `mocked_create_metrics_documentation_parent_page`: To simulate
                the root page not being found

        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()
        mocked_create_metrics_documentation_parent_page.side_effect = [
            HomePage.DoesNotExist
        ]

        # When
        forward_migration_metrics_documentation_parent_page(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        expected_log = "No Root page available to create metrics docs parent page with"
        assert expected_log in caplog.text


class TestForwardMigrationMetricsDocumentationChildEntries:
    @mock.patch(f"{MODULE_PATH}.create_metrics_documentation_child_entries")
    def test_delegates_call_successfully(
        self, spy_create_metrics_documentation_child_entries: mock.MagicMock
    ):
        """
        Given mocked django objects for the apps and schema editor
        When `forward_migration_metrics_documentation_child_entries()` is called
        Then the call is delegated to `create_metrics_documentation_child_entries()`

        Patches:
            `spy_create_metrics_documentation_parent_page`: For the main assertion

        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()

        # When
        forward_migration_metrics_documentation_child_entries(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        spy_create_metrics_documentation_child_entries.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.create_metrics_documentation_child_entries")
    def test_records_log_when_no_root_page_exists(
        self,
        mocked_create_metrics_documentation_child_entries: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given mocked django objects for the apps and schema editor
        And a `MetricsDocumentationParentPage.DoesNotExist` error
            which is thrown when trying to create child entries
        When `forward_migration_metrics_documentation_child_entries()` is called
        Then the call is delegated to `create_metrics_documentation_parent_page()`

        Patches:
            `mocked_create_metrics_documentation_child_entries`: To simulate
                the root page not being found

        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()
        mocked_create_metrics_documentation_child_entries.side_effect = [
            MetricsDocumentationParentPage.DoesNotExist
        ]

        # When
        forward_migration_metrics_documentation_child_entries(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        expected_log = (
            "No metrics docs parent page available to create child entries with"
        )
        assert expected_log in caplog.text


class TestReverseMigrationMetricsDocumentationChildEntries:
    @mock.patch(f"{MODULE_PATH}.remove_metrics_documentation_child_entries")
    def test_delegates_call_successfully(
        self, spy_remove_metrics_documentation_child_entries: mock.MagicMock
    ):
        """
        Given mocked django objects for the apps and schema editor
        When `reverse_migration_metrics_documentation_child_entries()` is called
        Then the call is delegated to `remove_metrics_documentation_child_entries()`

        Patches:
            `spy_remove_metrics_documentation_child_entries`: For the main assertion

        """
        # Given
        mocked_apps = mock.Mock()
        mocked_schema_editor = mock.Mock()

        # When
        reverse_migration_metrics_documentation_child_entries(
            apps=mocked_apps,
            schema_editor=mocked_schema_editor,
        )

        # Then
        spy_remove_metrics_documentation_child_entries.assert_called_once()
